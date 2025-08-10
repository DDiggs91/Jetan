// app/static/js/autoplay.js
import { API } from "./api.js";
import { State, status } from "./state.js";
import { refresh } from "./main.js";

export function toggleAutoplay(btn){
  if (!State.GID) return;
  if (State.AUTO){
    clearInterval(State.AUTO);
    State.AUTO = null;
    btn.textContent = "Auto-play (random)";
    status("Auto-play stopped.");
    return;
  }
  btn.textContent = "Stop auto-play";
  status("Auto-play started (random legal moves).");
  State.AUTO = setInterval(async () => {
    try {
      await refresh();
      const S = State.SNAPSHOT;
      if (!S || S.result){
        clearInterval(State.AUTO); State.AUTO=null; btn.textContent="Auto-play (random)"; return;
      }
      const toMove = (S.toMove || "").toLowerCase();
      const mySquares = S.pieces.filter(p => p.color.toLowerCase() === toMove).map(p => p.square);
      const moves = [];
      for (const sq of mySquares){
        const r = await API.legal(State.GID, sq.row, sq.col);
        if (!r.ok) continue;
        const js = await r.json();
        for (const d of js.destinations) moves.push({ from:{row:sq.row, col:sq.col}, to:d });
      }
      if (moves.length === 0){
        clearInterval(State.AUTO); State.AUTO=null; btn.textContent="Auto-play (random)"; status("No legal moves; stopping."); return;
      }
      const choice = moves[Math.floor(Math.random()*moves.length)];
      const m = await API.move(State.GID, State.VERSION, choice);
      if (m.status === 200){
        State.VERSION = parseInt(m.headers.get("ETag")) || State.VERSION;
        State.lastMove = choice;
      } else {
        await refresh();
      }
    } catch (e) { /* ignore */ }
  }, 600);
}
