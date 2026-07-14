from __future__ import annotations

import pickle
from types import SimpleNamespace

import pytest

from src.app import create_app


@pytest.fixture()
def app(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "match-summary.txt").write_text(
        "Defensa de Hierro: arco en cero.", encoding="utf-8"
    )
    return create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test.db"),
            "REPORT_DIR": str(reports),
        }
    )


@pytest.fixture()
def client(app):
    return app.test_client()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_player_search(client):
    response = client.get("/players/search?name=Lucia")
    assert response.status_code == 200
    assert response.get_json()[0]["position"] == "Defensa central"


def test_ping(client, monkeypatch):
    def fake_run(command, **kwargs):
        assert "127.0.0.1" in command
        return SimpleNamespace(stdout="PING OK")

    monkeypatch.setattr("src.app.subprocess.run", fake_run)
    response = client.get("/system/ping?target=127.0.0.1")
    assert response.status_code == 200
    assert response.get_json()["output"] == "PING OK"


def test_read_report(client):
    response = client.get("/reports/read?file=match-summary.txt")
    assert response.status_code == 200
    assert "arco en cero" in response.get_data(as_text=True)


def test_import_tactics(client):
    payload = pickle.dumps(
        {"formation": "4-4-2", "players": ["Lucia Acero", "Mateo Muralla"]}
    )
    response = client.post(
        "/tactics/import", data=payload, content_type="application/octet-stream"
    )
    assert response.status_code == 200
    assert response.get_json()["imported"] is True


def test_welcome(client):
    response = client.get("/fans/welcome?name=Leonardo")
    assert response.status_code == 200
    assert "Bienvenido Leonardo" in response.get_data(as_text=True)
