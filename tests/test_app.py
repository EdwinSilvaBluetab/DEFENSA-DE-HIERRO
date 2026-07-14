from __future__ import annotations

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


def test_sql_injection_is_treated_as_text(client):
    response = client.get("/players/search", query_string={"name": "' OR 1=1 --"})
    assert response.status_code == 200
    assert response.get_json() == []


def test_ping_uses_validated_argument_list(client, monkeypatch):
    def fake_run(command, **kwargs):
        assert command == ["ping", "-c", "1", "127.0.0.1"]
        assert kwargs["shell"] is False
        return SimpleNamespace(stdout="PING OK")

    monkeypatch.setattr("src.app.subprocess.run", fake_run)
    response = client.get("/system/ping?target=127.0.0.1")
    assert response.status_code == 200
    assert response.get_json()["output"] == "PING OK"


def test_command_injection_is_rejected(client, monkeypatch):
    called = False

    def fake_run(*args, **kwargs):
        nonlocal called
        called = True
        return SimpleNamespace(stdout="unexpected")

    monkeypatch.setattr("src.app.subprocess.run", fake_run)
    response = client.get(
        "/system/ping", query_string={"target": "127.0.0.1; echo blocked"}
    )
    assert response.status_code == 400
    assert called is False


def test_read_report(client):
    response = client.get("/reports/read?file=match-summary.txt")
    assert response.status_code == 200
    assert "arco en cero" in response.get_data(as_text=True)


def test_path_traversal_is_rejected(client):
    response = client.get("/reports/read", query_string={"file": "../../test.db"})
    assert response.status_code == 400


def test_import_tactics(client):
    response = client.post(
        "/tactics/import",
        json={"formation": "4-4-2", "players": ["Lucia Acero", "Mateo Muralla"]},
    )
    assert response.status_code == 200
    assert response.get_json()["imported"] is True


def test_binary_deserialization_payload_is_rejected(client):
    response = client.post(
        "/tactics/import",
        data=b"not-json-and-never-unpickled",
        content_type="application/octet-stream",
    )
    assert response.status_code == 400


def test_welcome(client):
    response = client.get("/fans/welcome?name=Leonardo")
    assert response.status_code == 200
    assert "Bienvenido Leonardo" in response.get_data(as_text=True)


def test_xss_is_escaped(client):
    response = client.get(
        "/fans/welcome", query_string={"name": "<script>alert(1)</script>"}
    )
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<script>" not in body
    assert "&lt;script&gt;" in body
