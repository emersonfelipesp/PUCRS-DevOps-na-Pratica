# Estágio de build: instala as dependências em um prefixo isolado.
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements-runtime.lock ./requirements.txt
RUN pip install --no-cache-dir --require-hashes --prefix=/install -r requirements.txt

# Estágio final: imagem enxuta, sem compiladores e sem cache de pacotes.
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="inventario-rede" \
      org.opencontainers.image.description="API de inventário de equipamentos de rede" \
      org.opencontainers.image.source="https://github.com/emersonfelipesp/PUCRS-DevOps-na-Pratica"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_PORT=8000

# A aplicação nunca roda como root: o usuário é criado sem shell e sem senha.
RUN groupadd --gid 10001 inventario \
    && useradd --uid 10001 --gid inventario --shell /usr/sbin/nologin --create-home inventario

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app ./app

USER inventario

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
