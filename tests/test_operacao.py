"""Testes dos endpoints operacionais consumidos pela infraestrutura."""

from fastapi.testclient import TestClient

from app import __version__


def test_health_responde_ok(client: TestClient) -> None:
    """O healthcheck usado pelo container deve responder 200 e a versão."""
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == __version__
    assert body["devices"] == 0


def test_metrics_exposto_no_formato_prometheus(client: TestClient) -> None:
    """O endpoint /metrics deve devolver as séries no formato de exposição."""
    client.get("/health")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "inventario_http_requests_total" in response.text


def test_documentacao_openapi_disponivel(client: TestClient) -> None:
    """O contrato OpenAPI precisa estar publicado para consumo dos clientes."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/devices" in response.json()["paths"]
