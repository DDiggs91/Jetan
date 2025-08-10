// app/static/js/api.js
export const API = {
  create: () => fetch("/api/v1/games", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ variant: "standard" })
  }),
  snapshot: (gid) => fetch(`/api/v1/games/${gid}`),
  join: (gid, seat) => fetch(`/api/v1/games/${gid}/join`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seat })
  }),
  legal: (gid, row, col) => fetch(`/api/v1/games/${gid}/legal?row=${row}&col=${col}`),
  move: (gid, version, payload) => fetch(`/api/v1/games/${gid}/moves`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "If-Match": String(version) },
    body: JSON.stringify(payload)
  }),
  diffs: (gid, since) => fetch(`/api/v1/games/${gid}/diffs?since=${since}`),
  control: (gid, action) => fetch(`/api/v1/games/${gid}/controls`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action })
  }),
};

export function versionFrom(res, js) {
  // Avoid mixing ?? with || in the same expression: be explicit.
  const fromBody = js && Object.prototype.hasOwnProperty.call(js, "version") ? js.version : null;
  if (fromBody !== null && fromBody !== undefined) return fromBody;
  const etag = parseInt(res.headers.get("ETag"));
  return Number.isFinite(etag) ? etag : 0;
}
