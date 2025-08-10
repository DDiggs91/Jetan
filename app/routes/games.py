from __future__ import annotations
from flask import Blueprint, request, jsonify, current_app, abort, make_response

bp = Blueprint("games", __name__, url_prefix="/api/v1/games")


@bp.post("")
def create_game():
    payload = request.get_json(force=True, silent=False) or {}
    variant = payload.get("variant", "standard")
    time = payload.get("time") or {"initialSec": 600, "incrementSec": 0}
    seats = payload.get("seats") or {"orange": "human", "black": "human"}

    svc = current_app.extensions["game_service"]
    game_id, version, snapshot = svc.create_game(variant=variant, time_dict=time, seats=seats)

    resp = make_response(jsonify({"gameId": game_id, "version": version, "state": snapshot}), 201)
    resp.headers["ETag"] = str(version)
    return resp


@bp.get("/<game_id>")
def get_game(game_id: str):
    svc = current_app.extensions["game_service"]
    version, snapshot = svc.get_snapshot(game_id)
    resp = make_response(jsonify({"gameId": game_id, "version": version, "state": snapshot}), 200)
    resp.headers["ETag"] = str(version)
    return resp


@bp.post("/<game_id>/join")
def join_game(game_id: str):
    payload = request.get_json(force=True, silent=False) or {}
    seat = payload.get("seat")
    if seat not in ("orange", "black", None):
        abort(400, description="Invalid seat")

    svc = current_app.extensions["game_service"]
    out = svc.join_game(game_id, seat)  # returns {"seat": "orange"} or raises
    return jsonify(out), 200


@bp.post("/<game_id>/controls")
def controls(game_id: str):
    payload = request.get_json(force=True, silent=False) or {}
    action = payload.get("action")
    if action not in ("resign", "offer_draw", "accept_draw", "decline_draw"):
        abort(400, description="Invalid control action")

    svc = current_app.extensions["game_service"]
    result = svc.apply_control(game_id, action)
    return jsonify(result), 200
