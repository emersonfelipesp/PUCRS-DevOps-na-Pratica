"""Testes do ciclo de vida dos equipamentos de rede."""

from fastapi.testclient import TestClient


def test_inventario_inicia_vazio(client: TestClient) -> None:
    """Sem carga inicial, a listagem deve devolver uma coleção vazia."""
    response = client.get("/api/v1/devices")

    assert response.status_code == 200
    assert response.json() == []


def test_cria_e_recupera_equipamento(client: TestClient, device_payload: dict[str, str]) -> None:
    """Um equipamento criado deve ser recuperável pelo identificador."""
    created = client.post("/api/v1/devices", json=device_payload)

    assert created.status_code == 201
    device_id = created.json()["id"]

    fetched = client.get(f"/api/v1/devices/{device_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "rtr-lab-01"
    assert fetched.json()["management_ip"] == "10.0.0.1"


def test_nome_e_normalizado(client: TestClient, device_payload: dict[str, str]) -> None:
    """Nomes com espaços e maiúsculas devem ser normalizados na criação."""
    device_payload["name"] = "  RTR-LAB-02  "

    response = client.post("/api/v1/devices", json=device_payload)

    assert response.status_code == 201
    assert response.json()["name"] == "rtr-lab-02"


def test_nome_duplicado_e_recusado(client: TestClient, device_payload: dict[str, str]) -> None:
    """O inventário não pode aceitar dois equipamentos com o mesmo nome."""
    client.post("/api/v1/devices", json=device_payload)

    response = client.post("/api/v1/devices", json=device_payload)

    assert response.status_code == 409


def test_ip_invalido_e_recusado(client: TestClient, device_payload: dict[str, str]) -> None:
    """Endereços fora do formato IPv4 devem ser barrados na validação."""
    device_payload["management_ip"] = "10.0.0.300"

    response = client.post("/api/v1/devices", json=device_payload)

    assert response.status_code == 422


def test_papel_invalido_e_recusado(client: TestClient, device_payload: dict[str, str]) -> None:
    """Somente os papéis previstos no enum são aceitos."""
    device_payload["role"] = "impressora"

    response = client.post("/api/v1/devices", json=device_payload)

    assert response.status_code == 422


def test_filtra_por_site_e_status(client: TestClient, device_payload: dict[str, str]) -> None:
    """Os filtros de listagem devem restringir o conjunto retornado."""
    client.post("/api/v1/devices", json=device_payload)
    client.post(
        "/api/v1/devices",
        json={
            "name": "sw-lab-01",
            "role": "switch",
            "site": "matriz",
            "management_ip": "10.0.0.2",
            "status": "offline",
        },
    )

    por_site = client.get("/api/v1/devices", params={"site": "matriz"})
    por_status = client.get("/api/v1/devices", params={"status": "active"})

    assert [device["name"] for device in por_site.json()] == ["sw-lab-01"]
    assert [device["name"] for device in por_status.json()] == ["rtr-lab-01"]


def test_atualizacao_parcial(client: TestClient, device_payload: dict[str, str]) -> None:
    """A atualização parcial altera somente os campos enviados."""
    device_id = client.post("/api/v1/devices", json=device_payload).json()["id"]

    response = client.patch(f"/api/v1/devices/{device_id}", json={"status": "decommissioned"})

    assert response.status_code == 200
    assert response.json()["status"] == "decommissioned"
    assert response.json()["site"] == "laboratorio"


def test_remocao_de_equipamento(client: TestClient, device_payload: dict[str, str]) -> None:
    """Após a remoção, o equipamento deixa de ser encontrado."""
    device_id = client.post("/api/v1/devices", json=device_payload).json()["id"]

    removed = client.delete(f"/api/v1/devices/{device_id}")

    assert removed.status_code == 204
    assert client.get(f"/api/v1/devices/{device_id}").status_code == 404


def test_equipamento_inexistente_retorna_404(client: TestClient) -> None:
    """Operações sobre identificadores inexistentes devem devolver 404."""
    assert client.get("/api/v1/devices/999").status_code == 404
    assert client.patch("/api/v1/devices/999", json={"status": "active"}).status_code == 404
    assert client.delete("/api/v1/devices/999").status_code == 404
