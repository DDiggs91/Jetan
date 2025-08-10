"""
Random self-play client demonstrating how to use the API from an external system.

Usage:
  python clients/random_bot.py

This script will create a game, then repeatedly query /legal to pick random legal moves
for the side to move, until no legal moves remain.
"""
import time, random, requests

BASE = "http://127.0.0.1:5000"

def create_game():
    r = requests.post(f"{BASE}/api/v1/games", json={"variant":"standard"})
    r.raise_for_status()
    js = r.json()
    gid = js["gameId"]
    version = int(r.headers.get("ETag", js.get("version", 0)))
    return gid, version

def snapshot(gid):
    r = requests.get(f"{BASE}/api/v1/games/{gid}")
    r.raise_for_status()
    js = r.json()
    return js, int(r.headers.get("ETag", js.get("version", 0)))

def legal(gid, row, col):
    r = requests.get(f"{BASE}/api/v1/games/{gid}/legal", params={"row":row, "col":col})
    if r.status_code != 200:
        return [], None
    js = r.json()
    return js.get("destinations", []), int(r.headers.get("ETag", js.get("version", 0)))

def move(gid, version, payload):
    r = requests.post(f"{BASE}/api/v1/games/{gid}/moves", headers={"If-Match": str(version)}, json=payload)
    if r.status_code != 200:
        return None, version
    return r.json(), int(r.headers.get("ETag", version))

def main():
    gid, ver = create_game()
    print("Created game:", gid, "version:", ver)
    while True:
        snap, ver = snapshot(gid)
        state = snap["state"]
        if state.get("result"):
            print("Game finished:", state["result"])
            break
        to_move = state["toMove"].lower()
        pieces = [p for p in state["pieces"] if p["color"].lower() == to_move]
        moves = []
        for p in pieces:
            dests, _ = legal(gid, p["square"]["row"], p["square"]["col"])
            for d in dests:
                moves.append({"from": p["square"], "to": d})
        if not moves:
            print("No legal moves. Stopping.")
            break
        choice = random.choice(moves)
        res, ver = move(gid, ver, choice)
        print("Move", choice, "-> ver", ver)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
