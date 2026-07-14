from __future__ import annotations

import ipaddress
import re
import sqlite3
import subprocess
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, make_response, request
from markupsafe import escape

_ALLOWED_FORMATIONS = {"4-4-2", "4-3-3", "3-5-2", "5-3-2"}
_MAX_PLAYERS = 23


def create_app(test_config: dict | None = None) -> Flask:
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
    def health():
        return jsonify(status="ok", component="iron-defense-api")

    @app.get("/players/search")
    def search_players():
        name = request.args.get("name", "")[:80]
        with sqlite3.connect(app.config["DATABASE"]) as connection:
            rows = connection.execute(
                "SELECT id, name, position FROM players WHERE name LIKE ?",
                (f"%{name}%",),
            ).fetchall()
        return jsonify(
            [
                {"id": row[0], "name": row[1], "position": row[2]}
                for row in rows
            ]
        )

    @app.get("/system/ping")
    def ping_host():
        target = request.args.get("target", "127.0.0.1")
        try:
            validated_ip = str(ipaddress.ip_address(target))
        except ValueError:
            return jsonify(error="target must be a valid IPv4 or IPv6 address"), 400

        result = subprocess.run(
            ["ping", "-c", "1", validated_ip],
            shell=False,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        return jsonify(target=validated_ip, output=result.stdout[-500:])

    @app.get("/reports/read")
    def read_report():
        filename = request.args.get("file", "match-summary.txt")
        safe_filename = Path(filename).name
        if (
            safe_filename != filename
            or safe_filename in {"", ".", ".."}
            or not re.fullmatch(r"[A-Za-z0-9._-]{1,120}", safe_filename)
        ):
            return jsonify(error="invalid report path"), 400

        base_dir = Path(app.config["REPORT_DIR"]).resolve()
        report_path = (base_dir / safe_filename).resolve()

        if report_path != base_dir and base_dir not in report_path.parents:
            return jsonify(error="invalid report path"), 400
        if not report_path.is_file():
            return jsonify(error="report not found"), 404

        return make_response(report_path.read_text(encoding="utf-8"), 200)

    @app.post("/tactics/import")
    def import_tactics():
        tactics = request.get_json(silent=True)
        validation_error = _validate_tactics(tactics)
        if validation_error:
            return jsonify(error=validation_error), 400
        return jsonify(imported=True, tactics=tactics)

    @app.get("/fans/welcome")
    def welcome_fan():
        fan_name = request.args.get("name", "Hincha")[:80]
        return make_response(f"<h1>Bienvenido {escape(fan_name)}</h1>")

    return app


def _validate_tactics(tactics: Any) -> str | None:
    if not isinstance(tactics, dict):
        return "request body must be a JSON object"

    formation = tactics.get("formation")
    players = tactics.get("players")

    if formation not in _ALLOWED_FORMATIONS:
        return "formation is not allowed"
    if not isinstance(players, list) or not 1 <= len(players) <= _MAX_PLAYERS:
        return "players must be a non-empty list with at most 23 entries"
    if not all(isinstance(player, str) and 1 <= len(player) <= 80 for player in players):
        return "each player must be a string between 1 and 80 characters"

    return None


def _initialize_storage(app: Flask) -> None:
    database_path = Path(app.config["DATABASE"])
    report_dir = Path(app.config["REPORT_DIR"])
    database_path.parent.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

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
        count = connection.execute("SELECT COUNT(*) FROM players").fetchone()[0]
        if count == 0:
            connection.executemany(
                "INSERT INTO players(name, position) VALUES (?, ?)",
                [
                    ("Lucia Acero", "Defensa central"),
                    ("Mateo Muralla", "Lateral derecho"),
                    ("Sara Candado", "Portera"),
                ],
            )


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000)
