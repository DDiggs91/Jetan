# app/services/game_service.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Optional
import threading
import time
import uuid

from app.static.constants import INITIAL_BOARD

# ---------- Domain-ish DTOs ----------
Square = Dict[str, int]  # {"row": int, "col": int}
Piece = Dict[str, Any]  # {"id": str, "type": str, "color": "ORANGE"|"BLACK", "square": Square}
State = Dict[str, Any]  # {"pieces":[Piece], "toMove": "ORANGE"|"BLACK", "result": Optional[str], "flags": {...}}


# ---------- Errors you can map in a central error handler ----------
class Conflict(Exception): ...  # 409


class BadAction(Exception): ...  # 400


class Finished(Exception): ...  # 410


class SeatError(Exception): ...  # 403


# ---------- Simple diff model ----------
@dataclass
class Diff:
    added: List[Piece] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)  # piece ids
    moved: List[Dict[str, Any]] = field(default_factory=list)  # {"id":..., "to": Square}
    flags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"added": self.added, "removed": self.removed, "moved": self.moved, "flags": self.flags}


# ---------- In-memory repo ----------
@dataclass
class GameRecord:
    game_id: str
    version: int
    state: State
    seats: Dict[str, Optional[str]]  # {"orange": None|"user", "black": None|"user"}
    events: List[Dict[str, Any]]  # append-only
    diffs: List[Dict[str, Any]]  # indexed by version step (v->v+1)
    clocks: Dict[str, int]  # naive seconds remaining
    last_turn_started_at: float


class InMemoryGameService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._games: Dict[str, GameRecord] = {}

    # ---- lifecycle ----
    def create_game(self, variant: str, time_dict: Dict[str, int], seats: Dict[str, str]) -> Tuple[str, int, State]:
        with self._lock:
            gid = f"g_{uuid.uuid4().hex[:8]}"
            initial_state: State = {
                "pieces": INITIAL_BOARD,
                "toMove": "ORANGE",
                "result": None,
                "flags": {
                    "princessEscapedOrange": False,
                    "princessEscapedBlack": False,
                },
            }
            rec = GameRecord(
                game_id=gid,
                version=0,
                state=initial_state,
                seats={"orange": None, "black": None},
                events=[],
                diffs=[],
                clocks={"orange": time_dict.get("initialSec", 600), "black": time_dict.get("initialSec", 600)},
                last_turn_started_at=time.time(),
            )
            self._games[gid] = rec
            return gid, rec.version, rec.state

    def get_snapshot(self, game_id: str) -> Tuple[int, State]:
        rec = self._must(game_id)
        return rec.version, rec.state

    def join_game(self, game_id: str, seat: Optional[str]) -> Dict[str, Any]:
        rec = self._must(game_id)
        if seat is None:
            return {"seat": None}
        seat = seat.lower()
        if seat not in ("orange", "black"):
            raise SeatError("invalid seat")
        with self._lock:
            if rec.seats[seat] is not None:
                raise SeatError("seat taken")
            rec.seats[seat] = f"anon-{uuid.uuid4().hex[:6]}"
        return {"seat": seat}

    def apply_control(self, game_id: str, action: str) -> Dict[str, Any]:
        rec = self._must(game_id)
        if rec.state["result"] is not None:
            raise Finished("game already finished")
        if action == "resign":
            winner = "BLACK" if rec.state["toMove"] == "ORANGE" else "ORANGE"
            rec.state["result"] = f"resign_{rec.state['toMove'].lower()}"
            return {"result": rec.state["result"], "winner": winner}
        raise BadAction("unsupported control action")

    # ---- rules helpers (stubbed) ----
    def legal_destinations(self, game_id: str, from_sq: Square) -> Tuple[int, Square, List[Square]]:
        rec = self._must(game_id)
        # engine hook goes here — for now return empty list
        return rec.version, {"row": from_sq["row"], "col": from_sq["col"]}, []

    # ---- apply move with versioning ----
    def apply_move(
        self, game_id: str, expected_version: int, move_payload: Dict[str, Any], idem_key: Optional[str]
    ) -> Tuple[Dict[str, Any], int, List[Dict[str, Any]], Dict[str, int]]:
        rec = self._must(game_id)
        with self._lock:
            if rec.version != expected_version:
                raise Conflict(f"version {expected_version} != {rec.version}")

            # naive time accounting (server-trust)
            self._tick_clocks(rec)

            if move_payload.get("action") != "move":
                raise BadAction("only 'move' supported")

            src = move_payload.get("from")
            dst = move_payload.get("to")
            if not self._valid_square(src) or not self._valid_square(dst):
                raise BadAction("invalid square")

            # engine: find piece at src (by position)
            piece = self._find_piece_at(rec.state, src)
            if not piece:
                raise BadAction("no piece at source")

            # (engine legality would be here — skipped in this stub)

            diff = Diff()
            # capture if enemy at dst
            cap = self._find_piece_at(rec.state, dst)
            if cap:
                diff.removed.append(cap["id"])
                rec.state["pieces"] = [p for p in rec.state["pieces"] if p["id"] != cap["id"]]

            # move piece (mutate its square)
            piece["square"] = {"row": dst["row"], "col": dst["col"]}
            diff.moved.append({"id": piece["id"], "to": piece["square"]})

            # flip turn, bump version, append diff/event
            rec.state["toMove"] = "BLACK" if rec.state["toMove"] == "ORANGE" else "ORANGE"
            rec.version += 1
            rec.diffs.append(diff.to_dict())
            rec.events.append({"type": "move", "from": src, "to": dst, "v": rec.version})
            # reset turn start
            rec.last_turn_started_at = time.time()

            return diff.to_dict(), rec.version, [], dict(rec.clocks)

    # ---- incremental sync ----
    def get_diffs(self, game_id: str, since_version: int) -> Dict[str, Any]:
        rec = self._must(game_id)
        if since_version < 0 or since_version > rec.version:
            raise Conflict("bad since version")
        if since_version == rec.version:
            return {"fromVersion": since_version, "toVersion": rec.version, "diffs": []}
        # diffs are stored as v->v+1 in order
        start = since_version
        return {"fromVersion": since_version, "toVersion": rec.version, "diffs": rec.diffs[start:]}

    # ---- helpers ----
    def _must(self, game_id: str) -> GameRecord:
        rec = self._games.get(game_id)
        if not rec:
            raise BadAction("unknown game")
        return rec

    def _find_piece_at(self, state: State, sq: Square) -> Optional[Piece]:
        for p in state["pieces"]:
            s = p["square"]
            if s["row"] == sq["row"] and s["col"] == sq["col"]:
                return p
        return None

    def _valid_square(self, sq: Any) -> bool:
        try:
            r, c = int(sq["row"]), int(sq["col"])
            return 0 <= r < 10 and 0 <= c < 10
        except Exception:
            return False

    def _tick_clocks(self, rec: GameRecord) -> None:
        now = time.time()
        elapsed = int(now - rec.last_turn_started_at)
        side = rec.state["toMove"].lower()
        if side in rec.clocks:
            rec.clocks[side] = max(0, rec.clocks[side] - elapsed)
        # no increments in this stub
