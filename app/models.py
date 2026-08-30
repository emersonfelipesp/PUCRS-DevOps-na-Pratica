"""Modelos de dados da API de inventário."""

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


def validate_ipv4(value: str) -> str:
    """Valida um endereço IPv4 em notação decimal pontuada."""
    octets = value.split(".")
    if len(octets) != 4:
        raise ValueError("management_ip deve estar no formato IPv4")
    for octet in octets:
        if not octet.isdigit() or not 0 <= int(octet) <= 255:
            raise ValueError("management_ip deve estar no formato IPv4")
    return value


class DeviceStatus(str, Enum):
    """Situação operacional de um equipamento."""

    ACTIVE = "active"
    PLANNED = "planned"
    OFFLINE = "offline"
    DECOMMISSIONED = "decommissioned"


class DeviceRole(str, Enum):
    """Papel do equipamento dentro da topologia."""

    ROUTER = "router"
    SWITCH = "switch"
    OLT = "olt"
    FIREWALL = "firewall"
    SERVER = "server"


class DeviceCreate(BaseModel):
    """Payload aceito na criação de um equipamento."""

    name: str = Field(min_length=1, max_length=64)
    role: DeviceRole
    site: str = Field(min_length=1, max_length=64)
    management_ip: str = Field(min_length=7, max_length=15)
    status: DeviceStatus = DeviceStatus.PLANNED

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Remove espaços nas bordas e padroniza o nome em minúsculas."""
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("name não pode ser vazio")
        return normalized

    @field_validator("management_ip")
    @classmethod
    def check_management_ip(cls, value: str) -> str:
        """Garante que o endereço de gerência seja um IPv4 válido."""
        return validate_ipv4(value)


class DeviceUpdate(BaseModel):
    """Payload aceito na atualização parcial de um equipamento."""

    site: str | None = Field(default=None, min_length=1, max_length=64)
    management_ip: str | None = None
    status: DeviceStatus | None = None

    @field_validator("management_ip")
    @classmethod
    def check_management_ip(cls, value: str | None) -> str | None:
        """Reaproveita a validação de IPv4 quando o campo é informado."""
        if value is None:
            return None
        return validate_ipv4(value)


class Device(DeviceCreate):
    """Equipamento já persistido, com identificador e data de criação."""

    id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class HealthResponse(BaseModel):
    """Resposta do endpoint de saúde usada pelo healthcheck do container."""

    status: str
    version: str
    devices: int
