"""Aplicação FastAPI do inventário de rede."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app import __version__
from app.models import Device, DeviceCreate, DeviceUpdate, HealthResponse
from app.observability import configure_logging, observability_middleware
from app.storage import DuplicateDeviceError, repository


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Configura o logging e carrega a carga inicial de equipamentos."""
    configure_logging(os.getenv("LOG_LEVEL", "INFO"))
    if os.getenv("SEED_DEVICES", "true").lower() == "true":
        repository.seed()
    yield
    repository.clear()


app = FastAPI(
    title="Inventário de Rede",
    description=(
        "API de inventário de equipamentos de rede usada como aplicação de "
        "referência do projeto da disciplina DevOps na Prática."
    ),
    version=__version__,
    lifespan=lifespan,
)
app.middleware("http")(observability_middleware)


@app.get("/health", response_model=HealthResponse, tags=["operacao"])
def health() -> HealthResponse:
    """Informa a saúde do serviço, consumida pelo healthcheck do container."""
    return HealthResponse(status="ok", version=__version__, devices=repository.count())


@app.get("/metrics", tags=["operacao"])
def metrics() -> Response:
    """Expõe as métricas no formato de exposição do Prometheus."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/v1/devices", response_model=list[Device], tags=["devices"])
def list_devices(site: str | None = None, status: str | None = None) -> list[Device]:
    """Lista os equipamentos cadastrados, com filtros opcionais."""
    return repository.list(site=site, status=status)


@app.get("/api/v1/devices/{device_id}", response_model=Device, tags=["devices"])
def get_device(device_id: int) -> Device:
    """Retorna um equipamento específico."""
    device = repository.get(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="equipamento não encontrado")
    return device


@app.post(
    "/api/v1/devices",
    response_model=Device,
    status_code=status.HTTP_201_CREATED,
    tags=["devices"],
)
def create_device(payload: DeviceCreate) -> Device:
    """Cadastra um novo equipamento."""
    try:
        return repository.create(payload)
    except DuplicateDeviceError as error:
        raise HTTPException(
            status_code=409, detail="já existe equipamento com esse nome"
        ) from error


@app.patch("/api/v1/devices/{device_id}", response_model=Device, tags=["devices"])
def update_device(device_id: int, payload: DeviceUpdate) -> Device:
    """Atualiza parcialmente um equipamento existente."""
    device = repository.update(device_id, payload)
    if device is None:
        raise HTTPException(status_code=404, detail="equipamento não encontrado")
    return device


@app.delete(
    "/api/v1/devices/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["devices"],
)
def delete_device(device_id: int) -> Response:
    """Remove um equipamento do inventário."""
    if not repository.delete(device_id):
        raise HTTPException(status_code=404, detail="equipamento não encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
