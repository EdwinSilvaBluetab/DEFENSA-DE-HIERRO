from __future__ import annotations

import ipaddress
import os
import sqlite3
import subprocess
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, make_response, request
from markupsafe import escape

_ALLOWED_FORMATIONS = {"4-4-2", "4-3-3", "3-5-2", "5-3-2"}
_ALLOWED_REPORTS = {"match-summary.txt"}
_MAX_PLAYERS = 23
_MAX_SEARCH_LENGTH = 80
_MAX_OUTPUT_LENGTH = 500


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)

    project_root = Path(__file__).resolve().parents[1]

    app.config.from_mapping(
        DATABASE=str(project_root / "data" / "defense.db"),
        REPORT_DIR=str(project_root / "data" / "reports"),
        MAX_CONTENT_LENGTH=16 * 1024,
    )

    if test_config:
        app.config.update(test_config)

    _initialize_storage(app)

    @app.get("/health")
    def health() -> Response:
        return jsonify(
            status="ok",
            component="iron-defense-api",
        )

    @app.get("/players/search")
    def search_players() -> Response:
        name = request.args.get("name", "", type=str).strip()[:_MAX_SEARCH_LENGTH]

        with sqlite3.connect(app.config["DATABASE"]) as connection:
            rows = connection.execute(
                """
                SELECT id, name, position
                FROM players
                WHERE name LIKE ?
                """,
                (f"%{name}%",),
            ).fetchall()

        players = [
            {
                "id": row[0],
                "name": row[1],
                "position": row[2],
            }
            for row in rows
        ]

        return jsonify(players)

    @app.get("/system/ping")
    def ping_host() -> tuple[Response, int] | Response:
        target = request.args.get(
            "target",
            "127.0.0.1",
            type=str,
        ).strip()

        try:
            validated_ip = str(ipaddress.ip_address(target))
        except ValueError:
            return (
                jsonify(
                    error="target must be a valid IPv4 or IPv6 address",
                ),
                400,
            )

        # Windows utiliza -n; Linux y macOS utilizan -c.
        count_argument = "-n" if os.name == "nt" else "-c"

        try:
            result = subprocess.run(
                ["ping", count_argument, "1", validated_ip],
                shell=False,
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return jsonify(error="ping operation timed out"), 504
        except OSError:
            app.logger.exception("Unable to execute ping")
            return jsonify(error="ping command is unavailable"), 500

        output = result.stdout[-_MAX_OUTPUT_LENGTH:]

        return jsonify(
            target=validated_ip,
            output=output,
        )

    @app.get("/reports/read")
    def read_report() -> tuple[Response, int] | Response:
        filename = request.args.get(
            "file",
            "match-summary.txt",
            type=str,
        ).strip()

        if filename not in _ALLOWED_REPORTS:
            return jsonify(error="report is not allowed"), 400

        report_path = _get_allowed_report_path(
            report_dir=app.config["REPORT_DIR"],
            filename=filename,
        )

        if not report_path.is_file():
            return jsonify(error="report not found"), 404

        try:
            report_content = report_path.read_text(encoding="utf-8")
        except OSError:
            app.logger.exception("Unable to read report")
            return jsonify(error="unable to read report"), 500

        return make_response(report_content, 200)

    @app.post("/tactics/import")
    def import_tactics() -> tuple[Response, int] | Response:
        tactics = request.get_json(silent=True)

        validation_error = _validate_tactics(tactics)

        if validation_error:
            return jsonify(error=validation_error), 400

        return jsonify(
            imported=True,
            tactics=tactics,
        )

    @app.get("/fans/welcome")
    def welcome_fan() -> Response:
        fan_name = request.args.get(
            "name",
            "Hincha",
            type=str,
        ).strip()[:_MAX_SEARCH_LENGTH]

        safe_fan_name = escape(fan_name)

        response = make_response(
            f"<h1>Bienvenido {safe_fan_name}</h1>",
            200,
        )
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        response.headers["X-Content-Type-Options"] = "nosniff"

        return response

    return app


def _get_allowed_report_path(
    report_dir: str,
    filename: str,
) -> Path:
    """
    Devuelve únicamente rutas de reportes previamente autorizados.

    La entrada del usuario no se concatena directamente con una ruta.
    Cada opción permitida corresponde a una ruta definida por la aplicación.
    """
    base_dir = Path(report_dir).resolve()

    if filename == "match-summary.txt":
        return base_dir / "match-summary.txt"

    # Protección adicional en caso de que la función sea invocada directamente.
    raise ValueError("report is not allowed")


def _validate_tactics(tactics: Any) -> str | None:
    if not isinstance(tactics, dict):
        return "request body must be a JSON object"

    formation = tactics.get("formation")
    players = tactics.get("players")

    if formation not in _ALLOWED_FORMATIONS:
        return "formation is not allowed"

    if not isinstance(players, list):
        return "players must be a list"

    if not 1 <= len(players) <= _MAX_PLAYERS:
        return "players must be a non-empty list with at most 23 entries"

    if not all(
        isinstance(player, str)
        and 1 <= len(player.strip()) <= _MAX_SEARCH_LENGTH
        for player in players
    ):
        return "each player must be a string between 1 and 80 characters"

    return None


def _initialize_storage(app: Flask) -> None:
    database_path = Path(app.config["DATABASE"]).resolve()
    report_dir = Path(app.config["REPORT_DIR"]).resolve()

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    report_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT NOT NULL
            )
            """
        )

        result = connection.execute(
            "SELECT COUNT(*) FROM players"
        ).fetchone()

        player_count = result[0] if result else 0

        if player_count == 0:
            connection.executemany(
                """
                INSERT INTO players(name, position)
                VALUES (?, ?)
                """,
                [
                    ("Lucia Acero", "Defensa central"),
                    ("Mateo Muralla", "Lateral derecho"),
                    ("Sara Candado", "Portera"),
                ],
            )

        connection.commit()


if __name__ == "__main__":
    application = create_app()
    application.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )