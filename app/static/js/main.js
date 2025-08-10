// app/static/js/main.js
import { API, versionFrom } from "./api.js";
import { Store } from "./state.js";
import { status, buildBoard, renderPieces, updateKv } from "./ui.js";
import { onDragStart, onDragEnd, onDrop } from "./board.js";

function $(id) { return document.getElementById(id); }

async function refresh() {
  if (!Store.GID) return;
  const res = await API.snapshot(Store.GID);
  if (!res.ok) return;
  const js = await res.json();
  Store.VERSION = versionFrom(res, js);
  Store.STATE = js.state;
  updateKv();
  renderPieces(onDragStart, onDragEnd);
}

function startPolling() {
  if (Store.POLL) clearInterval(Store.POLL);
  Store.POLL = setInterval(async () => {
    if (!Store.GID || Store.VERSION == null) return;
    try {
      const res = await API.diffs(Store.GID, Store.VERSION);
      if (res.status === 200) {
        const js = await res.json();
        if (js && js.toVersion && js.toVersion !== Store.VERSION) {
          Store.VERSION = js.toVersion;
          await refresh();
        }
      } else if (res.status === 409) {
        await refresh(); // need snapshot
      }
    } catch (e) { /* ignore transient */ }
  }, 1000);
}

async function createGame() {
  const res = await API.create();
  const js = await res.json();
  Store.GID = js.gameId;
  Store.VERSION = versionFrom(res, js);
  Store.STATE = js.state;
  $("gameIdInput").value = Store.GID;
  updateKv();
  status("Created game " + Store.GID, "good");
  startPolling();
  renderPieces(onDragStart, onDragEnd);
}

async function loadGame() {
  const gid = $("gameIdInput").value.trim();
  if (!gid) return status("Enter a game ID to load.", "bad");
  const res = await API.snapshot(gid);
  if (!res.ok) return status("Failed to load game " + gid + " (" + res.status + ")", "bad");
  const js = await res.json();
  Store.GID = js.gameId;
  Store.VERSION = versionFrom(res, js);
  Store.STATE = js.state;
  updateKv();
  status("Loaded game " + Store.GID, "good");
  startPolling();
  renderPieces(onDragStart, onDragEnd);
}

async function join(seat) {
  if (!Store.GID) return status("Create or load a game first.", "bad");
  const res = await API.join(Store.GID, seat);
  if (!res.ok) return status("Join failed: " + res.status, "bad");
  const js = await res.json();
  Store.SEAT = js.seat || seat;
  updateKv();
  status("Joined as " + Store.SEAT, "good");
  await refresh();
}

async function control(action) {
  if (!Store.GID) return status("No game.", "bad");
  const res = await API.control(Store.GID, action);
  if (!res.ok) return status("Control failed (" + res.status + ")", "bad");
  await refresh();
}

async function autoplayLoop() {
  if (!Store.GID) return;
  const btn = $("autoplayBtn");
  if (Store.AUTO) {
    clearInterval(Store.AUTO); Store.AUTO = null;
    btn.textContent = "Auto‑play (random)"; status("Auto‑play stopped.");
    return;
  }
  btn.textContent = "Stop auto‑play";
  status("Auto‑play started (random legal moves).");
  Store.AUTO = setInterval(async () => {
    try {
      await refresh();
      const st = Store.STATE;
      if (!st || st.result) {
        clearInterval(Store.AUTO); Store.AUTO = null;
        btn.textContent = "Auto‑play (random)";
        return;
      }
      const toMove = (st.toMove || "").toLowerCase();
      const mySquares = st.pieces.filter(p => p.color.toLowerCase() === toMove).map(p => p.square);
      const candidateMoves = [];
      for (const sq of mySquares) {
        const r = await API.legal(Store.GID, sq.row, sq.col);
        if (!r.ok) continue;
        const js = await r.json();
        for (const d of js.destinations) candidateMoves.push({ from: { row: sq.row, col: sq.col }, to: d });
      }
      if (candidateMoves.length === 0) {
        clearInterval(Store.AUTO); Store.AUTO = null;
        btn.textContent = "Auto‑play (random)"; status("No legal moves; stopping.");
        return;
      }
      const choice = candidateMoves[Math.floor(Math.random() * candidateMoves.length)];
      const m = await API.move(Store.GID, Store.VERSION, choice);
      if (m.status === 200) {
        Store.VERSION = parseInt(m.headers.get("ETag")) || Store.VERSION;
        Store.lastMove = choice;
      } else {
        await refresh();
      }
    } catch (e) {}
  }, 600);
}

function wireControls() {
  $("createBtn").onclick = createGame;
  $("loadBtn").onclick = loadGame;
  $("joinOrangeBtn").onclick = () => join("orange");
  $("joinBlackBtn").onclick = () => join("black");
  $("autoplayBtn").onclick = autoplayLoop;
  $("resignBtn").onclick = () => control("resign");
}

document.addEventListener("DOMContentLoaded", () => {
  wireControls();
  buildBoard(ev => onDrop(ev, refresh));
  status("Ready. Create or load a game.");
});
