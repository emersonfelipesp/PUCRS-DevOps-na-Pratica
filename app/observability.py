"""Logging estruturado e métricas Prometheus da aplicação."""

import json
import logging
import sys
import time
from collections.abc import Awaitable, Callable

from prometheus_client import Counter, Histogram
from starlette.requests import Request
from starlette.responses import Response

REQUESTS = Counter(
    "inventario_http_requests_total",
    "Total de requisições HTTP recebidas pela API.",
    ["method", "path", "status"],
)

LATENCY = Histogram(
    "inventario_http_request_duration_seconds",
    "Duração das requisições HTTP em segundos.",
    ["method", "path"],
)


class JsonFormatter(logging.Formatter):
    """Formata cada registro de log como uma linha JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Serializa o registro no formato consumido pelo agregador de logs."""
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for attribute in ("method", "path", "status", "duration_ms"):
            value = getattr(record, attribute, None)
            if value is not None:
                payload[attribute] = value
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    """Direciona todos os logs para stdout no formato JSON."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)


async def observability_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Registra métricas e um log estruturado para cada requisição."""
    started = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - started
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)

    REQUESTS.labels(request.method, path, str(response.status_code)).inc()
    LATENCY.labels(request.method, path).observe(duration)
    logging.getLogger("inventario.access").info(
        "requisicao concluida",
        extra={
            "method": request.method,
            "path": path,
            "status": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        },
    )
    return response
