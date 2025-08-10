from __future__ import annotations
from flask import Blueprint, request, jsonify, current_app, abort, make_response

bp = Blueprint("moves", __name__, url_prefix="/api/v1/games")


def _require_version():
    if_match = request.headers.get("If-Match")
    if if_match is None:
        abort(428, description="Missing If-Match header")  # 428 Precondition Required
    try:
        return int(if_match)
    except ValueError:
        abort(400, description="Bad If-Match")


@bp.get("/<game_id>/legal")
def legal_moves(game_id: str):
    # Query by square or pieceId; square is simplest to start
    try:
        row = int(request.args["row"])
        col = int(request.args["col"])
    except (KeyError, ValueError):
        abort(400, description="row and col query params required")

    svc = current_app.extensions["game_service"]
    version, from_sq, destinations = svc.legal_destinations(game_id, {"row": row, "col": col})
    resp = make_response(jsonify({"from": from_sq, "destinations": destinations, "version": version}), 200)
    resp.headers["ETag"] = str(version)
    return resp


@bp.post("/<game_id>/moves")
def apply_move(game_id: str):
    version = _require_version()
    payload = request.get_json(force=True, silent=False) or {}
    # Expected shape: {"action":"move","from":{"row":..,"col":..},"to":{"row":..,"col":..},"tags":[...]}
    action = payload.get("action")
    if action != "move":
        abort(400, description="Unsupported action")

    svc = current_app.extensions["game_service"]
    diff, new_version, events, clocks = svc.apply_move(
        game_id=game_id,
        expected_version=version,
        move_payload=payload,
        idem_key=request.headers.get("Idempotency-Key"),
    )

    resp = make_response(
        jsonify(
            {
                "applied": True,
                "version": new_version,
                "diff": diff,
                "events": events,
                "clocks": clocks,
            }
        ),
        200,
    )
    resp.headers["ETag"] = str(new_version)
    return resp
