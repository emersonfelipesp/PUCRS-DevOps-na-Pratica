#!/usr/bin/env bash
#
# Deploy da stack do inventário de rede a partir dos containers publicados.
#
# Uso:
#   ./scripts/deploy.sh <tag-da-imagem> [porta]
#
# O script é idempotente: pode ser executado quantas vezes for necessário sobre
# o mesmo host. Ele baixa a imagem indicada, sobe a stack com o Docker Compose,
# aguarda o healthcheck do container e valida a aplicação com o teste de fumaça.
# Qualquer falha interrompe a execução e dispara o rollback para a versão
# anterior, quando existir.

set -Eeuo pipefail

readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly REGISTRY_IMAGE="${REGISTRY_IMAGE:-ghcr.io/emersonfelipesp/pucrs-devops-na-pratica}"
readonly STATE_FILE="${PROJECT_ROOT}/.deploy-versao-anterior"
readonly HEALTH_TIMEOUT_SECONDS=90

IMAGE_TAG="${1:-latest}"
APP_PORT="${2:-8000}"

log() {
  printf '[%s] %s\n' "$(date --iso-8601=seconds)" "$*"
}

erro() {
  printf '[%s] ERRO: %s\n' "$(date --iso-8601=seconds)" "$*" >&2
}

verifica_dependencias() {
  for binario in docker curl; do
    if ! command -v "${binario}" >/dev/null 2>&1; then
      erro "dependência ausente: ${binario}"
      exit 1
    fi
  done

  if ! docker compose version >/dev/null 2>&1; then
    erro "o plugin 'docker compose' não está disponível"
    exit 1
  fi
}

aguarda_saude() {
  local decorrido=0

  log "aguardando o container ficar saudável (limite de ${HEALTH_TIMEOUT_SECONDS}s)"
  while [[ "${decorrido}" -lt "${HEALTH_TIMEOUT_SECONDS}" ]]; do
    local estado
    estado="$(docker inspect -f '{{.State.Health.Status}}' inventario-api 2>/dev/null || echo indisponivel)"

    case "${estado}" in
      healthy)
        log "container saudável após ${decorrido}s"
        return 0
        ;;
      unhealthy)
        erro "o container foi marcado como unhealthy"
        return 1
        ;;
    esac

    sleep 3
    decorrido=$((decorrido + 3))
  done

  erro "tempo esgotado aguardando o healthcheck"
  return 1
}

rollback() {
  if [[ ! -f "${STATE_FILE}" ]]; then
    erro "não há versão anterior registrada; a stack será derrubada"
    APP_IMAGE="${REGISTRY_IMAGE}:${IMAGE_TAG}" docker compose down --remove-orphans || true
    return
  fi

  local versao_anterior
  versao_anterior="$(cat "${STATE_FILE}")"
  erro "restaurando a versão anterior: ${versao_anterior}"
  APP_IMAGE="${versao_anterior}" APP_PORT="${APP_PORT}" \
    docker compose up -d --remove-orphans
}

main() {
  cd "${PROJECT_ROOT}"
  verifica_dependencias

  local imagem="${REGISTRY_IMAGE}:${IMAGE_TAG}"
  log "iniciando o deploy da imagem ${imagem} na porta ${APP_PORT}"

  local versao_atual
  versao_atual="$(docker inspect -f '{{.Config.Image}}' inventario-api 2>/dev/null || true)"
  if [[ -n "${versao_atual}" ]]; then
    printf '%s\n' "${versao_atual}" >"${STATE_FILE}"
    log "versão em execução registrada para rollback: ${versao_atual}"
  fi

  log "baixando a imagem do registro de containers"
  docker pull "${imagem}"

  log "aplicando a nova versão com o Docker Compose"
  APP_IMAGE="${imagem}" APP_PORT="${APP_PORT}" \
    docker compose up -d --remove-orphans

  if ! aguarda_saude; then
    rollback
    exit 1
  fi

  if ! "${PROJECT_ROOT}/scripts/smoke-test.sh" "http://127.0.0.1:${APP_PORT}"; then
    erro "o teste de fumaça falhou"
    rollback
    exit 1
  fi

  log "deploy concluído com sucesso: ${imagem}"
  docker image prune --force --filter "until=168h" >/dev/null 2>&1 || true
}

main "$@"
