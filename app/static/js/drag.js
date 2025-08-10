// app/static/js/drag.js
import { API, extractVersion } from "./api.js";
import { State, KV } from "./state.js";
import { renderPieces } from "./board.js";
import { refresh } from "./main.js";

let dragCtx = null;

export async function onDragStart(ev){
  const piece = ev.currentTarget;
  const row = parseInt(piece.dataset.row), col = parseInt(piece.dataset.col);
  dragCtx = { from: {row, col} };
  if (!State.GID) return;

  const res = await API.legal(State.GID, row, col);
  if (res.ok){
    const js = await res.json();
    State.VERSION = extractVersion(js, res, State.VERSION);
    KV.kvVer.textContent = State.VERSION;
    document.querySelectorAll(".sq").forEach(s => s.classList.remove("hint","legal"));
    for (const d of js.destinations){
      const sq = document.getElementById(`sq-${d.row}-${d.col}`);
      if (sq) sq.classList.add("legal");
    }
    const fromSq = document.getElementById(`sq-${row}-${col}`);
    fromSq && fromSq.classList.add("hint");
  }
}

export function onDragEnd(_ev){
  document.querySelectorAll(".sq").forEach(s => s.classList.remove("hint","legal"));
}

export async function onDrop(ev){
  ev.preventDefault();
  if (!dragCtx || !State.GID) return;
  const to = { row: parseInt(ev.currentTarget.dataset.row), col: parseInt(ev.currentTarget.dataset.col) };
  const payload = { from: dragCtx.from, to };
  const res = await API.move(State.GID, State.VERSION, payload);
  if (res.status === 200){
    const js = await res.json();
    State.VERSION = extractVersion(js, res, State.VERSION);
    KV.kvVer.textContent = State.VERSION;
    State.lastMove = payload;
    await refresh();
  }else if (res.status === 409){
    await refresh();
  }
  dragCtx = null;
}
