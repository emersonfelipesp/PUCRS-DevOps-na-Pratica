output "rede" {
  description = "Nome da rede Docker criada para o ambiente."
  value       = docker_network.inventario.name
}

output "containers" {
  description = "Nomes das instâncias da API provisionadas."
  value       = docker_container.api[*].name
}

output "urls" {
  description = "URLs de acesso ao healthcheck de cada instância."
  value       = [for c in docker_container.api : "http://localhost:${c.ports[0].external}/health"]
}
