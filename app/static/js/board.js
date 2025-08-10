// app/static/js/board.js
import { API, versionFrom } from "./api.js";
import { Store } from "./state.js";
import { status, renderPieces } from "./ui.js";

let dragCtx = null;

export async function onDragStart(ev) {
  const piece = ev.currentTarget;
  const row = parseInt(piece.dataset.row), col = parseInt(piece.dataset.col);
  dragCtx = { from: { row, col } };
  if (!Store.GID) return;

  const res = await API.legal(Store.GID, row, col);
  if (res.ok) {
    const js = await res.json();
    Store.VERSION = versionFrom(res, js);
    document.querySelectorAll(".sq").forEach(s => s.classList.remove("hint","legal"));
    for (const d of js.destinations) {
      const sq = document.getElementById(`sq-${d.row}-${d.col}`);
      if (sq) sq.classList.add("legal");
    }
    const fromSq = document.getElementById(`sq-${row}-${col}`);
    fromSq && fromSq.classList.add("hint");
  }
}

export function onDragEnd(_ev) {
  document.querySelectorAll(".sq").forEach(s => s.classList.remove("hint","legal"));
}

export async function onDrop(ev, refresh) {
  ev.preventDefault();
  if (!dragCtx || !Store.GID) return;
  const to = { row: parseInt(ev.currentTarget.dataset.row), col: parseInt(ev.currentTarget.dataset.col) };
  const payload = { from: dragCtx.from, to };
  const res = await API.move(Store.GID, Store.VERSION, payload);
  if (res.status === 200) {
    const js = await res.json();
    Store.VERSION = versionFrom(res, js);
    Store.lastMove = payload;
    await refresh();
    status("Move applied.", "good");
  } else if (res.status === 409) {
    await refresh();
    status("Version conflict. Synced.", "bad");
  } else {
    status("Move rejected (" + res.status + ").", "bad");
  }
  dragCtx = null;
}

export { renderPieces }; // re-export for convenience
