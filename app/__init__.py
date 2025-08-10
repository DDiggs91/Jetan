# app/__init__.py
from flask import Flask, render_template
from app.routes import games, moves, diffs
from app.services.game_service import InMemoryGameService


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    if config:
        app.config.update(config)

    app.extensions["game_service"] = InMemoryGameService()

    app.register_blueprint(games.bp)
    app.register_blueprint(moves.bp)
    app.register_blueprint(diffs.bp)

    # TODO: central error handlers mapping exceptions to JSON/status codes

    @app.get("/")
    def index():
        return render_template("index.html")

    return app
