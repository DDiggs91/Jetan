from __future__ import annotations
from flask import Blueprint, request, jsonify, current_app, abort

bp = Blueprint("diffs", __name__, url_prefix="/api/v1/games")


@bp.get("/<game_id>/diffs")
def get_diffs(game_id: str):
    try:
        since = int(request.args["since"])
    except (KeyError, ValueError):
        abort(400, description="since query param (int) required")

    svc = current_app.extensions["game_service"]
    result = svc.get_diffs(game_id, since_version=since)
    # result either: {"fromVersion":..., "toVersion":..., "diffs":[...] }
    # or raises a domain error that your error handler will map to 409 with "need":"snapshot"
    return jsonify(result), 200
