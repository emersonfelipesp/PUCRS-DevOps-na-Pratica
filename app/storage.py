"""Repositório em memória dos equipamentos de rede.

O objetivo do projeto é o fluxo de DevOps, e não a persistência em si, por isso
o armazenamento é mantido em memória e isolado atrás de uma classe. Trocar por
um banco relacional exigiria alterar apenas este módulo.
"""

from itertools import count
from threading import Lock

from app.models import Device, DeviceCreate, DeviceUpdate

SEED_DEVICES: list[dict[str, str]] = [
    {
        "name": "rtr-poa-01",
        "role": "router",
        "site": "porto-alegre",
        "management_ip": "10.0.30.1",
        "status": "active",
    },
    {
        "name": "sw-poa-01",
        "role": "switch",
        "site": "porto-alegre",
        "management_ip": "10.0.30.2",
        "status": "active",
    },
    {
        "name": "olt-cxs-01",
        "role": "olt",
        "site": "caxias-do-sul",
        "management_ip": "10.0.50.10",
        "status": "planned",
    },
]


class DuplicateDeviceError(Exception):
    """Levantada quando já existe um equipamento com o mesmo nome."""


class DeviceRepository:
    """Coleção de equipamentos protegida por lock para uso concorrente."""

    def __init__(self) -> None:
        """Inicializa a coleção vazia, a sequência de ids e o lock."""
        self._devices: dict[int, Device] = {}
        self._sequence = count(1)
        self._lock = Lock()

    def seed(self) -> None:
        """Carrega os equipamentos iniciais usados na demonstração."""
        for payload in SEED_DEVICES:
            self.create(DeviceCreate(**payload))

    def clear(self) -> None:
        """Esvazia o repositório e reinicia a sequência de identificadores."""
        with self._lock:
            self._devices.clear()
            self._sequence = count(1)

    def count(self) -> int:
        """Retorna a quantidade de equipamentos armazenados."""
        return len(self._devices)

    def list(self, site: str | None = None, status: str | None = None) -> list[Device]:
        """Lista equipamentos, opcionalmente filtrados por site e por status."""
        devices = list(self._devices.values())
        if site is not None:
            devices = [device for device in devices if device.site == site]
        if status is not None:
            devices = [device for device in devices if device.status.value == status]
        return sorted(devices, key=lambda device: device.id)

    def get(self, device_id: int) -> Device | None:
        """Retorna um equipamento pelo identificador, ou None se não existir."""
        return self._devices.get(device_id)

    def create(self, payload: DeviceCreate) -> Device:
        """Cria um equipamento, recusando nomes já utilizados."""
        with self._lock:
            if any(device.name == payload.name for device in self._devices.values()):
                raise DuplicateDeviceError(payload.name)
            device = Device(id=next(self._sequence), **payload.model_dump())
            self._devices[device.id] = device
            return device

    def update(self, device_id: int, payload: DeviceUpdate) -> Device | None:
        """Aplica uma atualização parcial e devolve o equipamento resultante."""
        with self._lock:
            device = self._devices.get(device_id)
            if device is None:
                return None
            changes = payload.model_dump(exclude_none=True)
            updated = device.model_copy(update=changes)
            self._devices[device_id] = updated
            return updated

    def delete(self, device_id: int) -> bool:
        """Remove um equipamento e informa se ele existia."""
        with self._lock:
            return self._devices.pop(device_id, None) is not None


repository = DeviceRepository()
