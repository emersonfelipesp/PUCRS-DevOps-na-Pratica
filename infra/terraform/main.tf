# Provisionamento do ambiente de execução do inventário de rede.
#
# A infraestrutura é descrita por completo neste diretório: rede isolada,
# imagem da aplicação e as instâncias da API. Nenhum recurso é criado à mão,
# de modo que o ambiente pode ser destruído e recriado de forma idêntica.

locals {
  nome_base = "inventario-${var.nome_ambiente}"

  etiquetas = {
    projeto   = "pucrs-devops-na-pratica"
    ambiente  = var.nome_ambiente
    gerenciad = "terraform"
  }
}

resource "docker_network" "inventario" {
  name   = "${local.nome_base}-net"
  driver = "bridge"

  dynamic "labels" {
    for_each = local.etiquetas
    content {
      label = labels.key
      value = labels.value
    }
  }
}

resource "docker_image" "api" {
  name         = var.imagem
  keep_locally = true
}

resource "docker_container" "api" {
  count = var.replicas

  name     = "${local.nome_base}-api-${count.index + 1}"
  image    = docker_image.api.image_id
  restart  = "unless-stopped"
  must_run = true

  env = [
    "LOG_LEVEL=${var.nivel_de_log}",
    "SEED_DEVICES=true",
  ]

  ports {
    internal = 8000
    external = var.porta_externa + count.index
  }

  networks_advanced {
    name = docker_network.inventario.name
  }

  healthcheck {
    test         = ["CMD", "python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"]
    interval     = "15s"
    timeout      = "3s"
    retries      = 3
    start_period = "10s"
  }

  # Endurecimento do container provisionado.
  privileged = false
  read_only  = true
  capabilities {
    drop = ["ALL"]
  }

  dynamic "labels" {
    for_each = local.etiquetas
    content {
      label = labels.key
      value = labels.value
    }
  }
}
