variable "name" {
  description = "Table Name"
}

variable "billing_mode" {
  description = "Billing Mode ON DEMAND/PROVISIONED"
}

variable "read_capacity" {
  description = "Read Capacity"
  type = number
}

variable "write_capacity" {
  description = "Write Capacity"
  type = number
}

variable "primary_index_attributes" {
  description = "Table key Attributes. Necessary to declare here any attribute used as hash or range key"
  type = list(object({
    name = string
    type = string
    key_type = string # Key type is hash or range
  }))
}

variable "local_secondary_indices_keys" {
  description = "Optional secondary keys to compose secondary local indices"
  type = list(object({
    name = string
    range_key = string
  }))
  default = []
}

variable "tags" {
  description = "The identification tags to assign to the resources"
  type = map(string)
}

variable "ttl_attribute" {
  description = "Attribute to store the time to Live of a document"
  default = null
}