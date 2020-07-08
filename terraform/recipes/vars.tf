variable "orders_source_code" {
  description = "Path to Orders zip package"
}

variable "shops_source_code" {
  description = "Path to Shops zip package"
}

variable "users_source_code" {
  description = "path to users zip package"
}

variable "couriers_source_code" {
  description = "Path to couriers zip package"
}

variable "tags" {
  description = "Tags to be propagated to all resources"
  type = map(string)

  default = {
    application = "all"
    environment = "production"
  }
}

variable "users_db_keys" {
  description = "The Key fields in users database"
  type = list(object({
    name = string
    type = string
    key_type = string # Key type is hash or range
  }))

  default = [{
    name = "ID"
    type = "S"
    key_type = "hash"
  }]
}

variable "shops_db_keys" {
  description = "The Key fields in shops database"
  type = list(object({
    name = string
    type = string
    key_type = string # Key type is hash or range
  }))

  default = [{
    name = "ID"
    type = "S"
    key_type = "hash"
  }]
}

variable "orders_db_keys" {
  description = "The Key fields in orders database"
  type = list(object({
    name = string
    type = string
    key_type = string # Key type is hash or range
  }))

  default = [{
    name = "ID"
    type = "S"
    key_type = "hash"
  }]
}

variable "couriers_db_keys" {
  description = "The Key fields in couriers database"
  type = list(object({
    name = string
    type = string
    key_type = string # Key type is hash or range
  }))

  default = [{
    name = "ID"
    type = "S"
    key_type = "hash"
  }]
}