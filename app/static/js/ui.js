// app/static/js/ui.js
import { Store, Abbrev } from "./state.js";

const statusEl = () => document.getElementById("status");
const boardEl  = () => document.getElementById("board");
const kvGame   = () => document.getElementById("kvGame");
const kvSeat   = () => document.getElementById("kvSeat");
const kvToMove = () => document.getElementById("kvToMove");
const kvVer    = () => document.getElementById("kvVer");

export function status(msg, cls) {
  const el = statusEl();
  el.textContent = msg;
  el.className = "status mono" + (cls ? " " + cls : "");
}

export function buildBoard(onDrop) {
  const el = boardEl();
  el.innerHTML = "";
  for (let r = 0; r < 10; r++) {
    for (let c = 0; c < 10; c++) {
      const sq = document.createElement("div");
      sq.className = "sq " + ((r + c) % 2 === 0 ? "light" : "dark");
      sq.id = `sq-${r}-${c}`;
      sq.dataset.row = r; sq.dataset.col = c;
      sq.addEventListener("dragover", ev => ev.preventDefault());
      sq.addEventListener("drop", onDrop);
      el.appendChild(sq);
    }
  }
}

export function renderPieces(onDragStart, onDragEnd) {
  document.querySelectorAll(".sq").forEach(sq => { sq.classList.remove("legal","hint","last"); sq.innerHTML = ""; });
  const st = Store.STATE;
  if (!st) return;
  if (Store.lastMove) {
    const a = document.getElementById(`sq-${Store.lastMove.from.row}-${Store.lastMove.from.col}`);
    const b = document.getElementById(`sq-${Store.lastMove.to.row}-${Store.lastMove.to.col}`);
    a && a.classList.add("last"); b && b.classList.add("last");
  }
  for (const p of st.pieces) {
    const sq = document.getElementById(`sq-${p.square.row}-${p.square.col}`);
    if (!sq) continue;
    const el = document.createElement("div");
    el.className = "piece " + (p.color === "ORANGE" ? "orange" : "black");
    el.textContent = Abbrev[p.type] || p.type.slice(0,2);
    el.draggable = !!(Store.SEAT && p.color.toLowerCase() === Store.SEAT);
    el.dataset.row = p.square.row;
    el.dataset.col = p.square.col;
    el.dataset.type = p.type;
    el.addEventListener("dragstart", onDragStart);
    el.addEventListener("dragend", onDragEnd);
    sq.appendChild(el);
  }
  kvToMove().textContent = st.toMove || "—";
}

export function updateKv() {
  kvGame().textContent = Store.GID || "—";
  kvSeat().textContent = Store.SEAT || "—";
  kvVer().textContent  = Store.VERSION ?? "—";
}
