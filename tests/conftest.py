"""Fixtures compartilhadas pelos testes automatizados."""

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

os.environ["SEED_DEVICES"] = "false"

from app.main import app  # noqa: E402
from app.storage import repository  # noqa: E402


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Cliente HTTP de teste com o repositório sempre vazio no início."""
    repository.clear()
    with TestClient(app) as test_client:
        yield test_client
    repository.clear()


@pytest.fixture
def device_payload() -> dict[str, str]:
    """Payload válido de criação usado em vários testes."""
    return {
        "name": "rtr-lab-01",
        "role": "router",
        "site": "laboratorio",
        "management_ip": "10.0.0.1",
        "status": "active",
    }
