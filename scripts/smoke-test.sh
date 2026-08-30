#!/usr/bin/env bash
#
# Teste de fumaça executado após cada deploy.
#
# Uso:
#   ./scripts/smoke-test.sh [url-base]
#
# Exercita os endpoints que representam o caminho crítico da aplicação e
# devolve código de saída diferente de zero na primeira divergência, o que faz
# o deploy.sh disparar o rollback.

set -Eeuo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"
FALHAS=0

verifica() {
  local descricao="$1"
  local metodo="$2"
  local caminho="$3"
  local esperado="$4"
  local corpo="${5:-}"

  local argumentos=(--silent --show-error --max-time 10 --output /dev/null
                    --write-out '%{http_code}' --request "${metodo}")
  if [[ -n "${corpo}" ]]; then
    argumentos+=(--header 'Content-Type: application/json' --data "${corpo}")
  fi

  local obtido
  obtido="$(curl "${argumentos[@]}" "${BASE_URL}${caminho}" || echo 000)"

  if [[ "${obtido}" == "${esperado}" ]]; then
    printf '  [OK]    %s -> %s\n' "${descricao}" "${obtido}"
  else
    printf '  [FALHA] %s -> esperado %s, obtido %s\n' "${descricao}" "${esperado}" "${obtido}"
    FALHAS=$((FALHAS + 1))
  fi
}

printf 'Teste de fumaça contra %s\n\n' "${BASE_URL}"

verifica "healthcheck responde" GET /health 200
verifica "métricas expostas" GET /metrics 200
verifica "contrato OpenAPI publicado" GET /openapi.json 200
verifica "listagem de equipamentos" GET /api/v1/devices 200
verifica "equipamento inexistente devolve 404" GET /api/v1/devices/9999 404
verifica "payload inválido é recusado" POST /api/v1/devices 422 '{"name":""}'
# O nome carrega o instante da execução para que o teste seja idempotente e
# possa ser repetido sobre o mesmo ambiente sem colidir com execuções anteriores.
NOME_TESTE="rtr-smoke-$(date +%s)-${RANDOM}"
verifica "criação de equipamento válido" POST /api/v1/devices 201 \
  "{\"name\":\"${NOME_TESTE}\",\"role\":\"router\",\"site\":\"homologacao\",\"management_ip\":\"10.0.99.1\",\"status\":\"active\"}"
verifica "nome duplicado é recusado" POST /api/v1/devices 409 \
  "{\"name\":\"${NOME_TESTE}\",\"role\":\"router\",\"site\":\"homologacao\",\"management_ip\":\"10.0.99.1\",\"status\":\"active\"}"

printf '\n'
if [[ "${FALHAS}" -gt 0 ]]; then
  printf 'Teste de fumaça reprovado: %s verificação(ões) falharam.\n' "${FALHAS}" >&2
  exit 1
fi

printf 'Teste de fumaça aprovado: todas as verificações passaram.\n'
