from __future__ import annotations

import pickle
import sqlite3
import subprocess
from pathlib import Path

from flask import Flask, jsonify, make_response, request


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    project_root = Path(__file__).resolve().parents[1]
    app.config.from_mapping(
        DATABASE=str(project_root / "data" / "defense.db"),
        REPORT_DIR=str(project_root / "data" / "reports"),
    )

    if test_config:
        app.config.update(test_config)

    _initialize_storage(app)

    @app.get("/health")
    def health():
        return jsonify(status="ok", component="iron-defense-api")

    @app.get("/players/search")
    def search_players():
        name = request.args.get("name", "")
        query = (
            "SELECT id, name, position FROM players "
            "WHERE name LIKE '%" + name + "%'"
        )
        with sqlite3.connect(app.config["DATABASE"]) as connection:
            rows = connection.execute(query).fetchall()
        return jsonify(
            [
                {"id": row[0], "name": row[1], "position": row[2]}
                for row in rows
            ]
        )

    @app.get("/system/ping")
    def ping_host():
        target = request.args.get("target", "127.0.0.1")
        result = subprocess.run(
            "ping -c 1 " + target,
            shell=True,
            capture_output=True,
            text=True,
            timeout=3,
        )
        return jsonify(target=target, output=result.stdout[-500:])

    @app.get("/reports/read")
    def read_report():
        filename = request.args.get("file", "match-summary.txt")
        report_path = Path(app.config["REPORT_DIR"]) / filename
        return make_response(report_path.read_text(encoding="utf-8"), 200)

    @app.post("/tactics/import")
    def import_tactics():
        tactics = pickle.loads(request.get_data())
        return jsonify(imported=True, tactics=tactics)

    @app.get("/fans/welcome")
    def welcome_fan():
        fan_name = request.args.get("name", "Hincha")
        return make_response("<h1>Bienvenido " + fan_name + "</h1>")

    return app


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
