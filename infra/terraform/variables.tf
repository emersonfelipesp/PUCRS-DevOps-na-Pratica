variable "docker_host" {
  description = "Endpoint do daemon Docker onde a infraestrutura será provisionada."
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "imagem" {
  description = "Imagem publicada no registro de containers que será executada."
  type        = string
  default     = "ghcr.io/emersonfelipesp/pucrs-devops-na-pratica:latest"
}

variable "nome_ambiente" {
  description = "Nome do ambiente provisionado, usado como prefixo dos recursos."
  type        = string
  default     = "homologacao"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.nome_ambiente))
    error_message = "O nome do ambiente deve conter apenas letras minúsculas, números e hífens."
  }
}

variable "porta_externa" {
  description = "Porta do host publicada para a API do inventário."
  type        = number
  default     = 8000

  validation {
    condition     = var.porta_externa > 1024 && var.porta_externa < 65536
    error_message = "A porta externa deve estar entre 1025 e 65535."
  }
}

variable "replicas" {
  description = "Quantidade de instâncias da API a serem provisionadas."
  type        = number
  default     = 1

  validation {
    condition     = var.replicas >= 1 && var.replicas <= 5
    error_message = "O número de réplicas deve estar entre 1 e 5."
  }
}

variable "nivel_de_log" {
  description = "Nível de log da aplicação."
  type        = string
  default     = "INFO"

  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR"], var.nivel_de_log)
    error_message = "O nível de log deve ser DEBUG, INFO, WARNING ou ERROR."
  }
}
