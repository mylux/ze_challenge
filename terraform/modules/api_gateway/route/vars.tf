variable "api_id" {
  description = "The API Gateway (rest) id"
}

variable "parent_id" {
  description = "The parent route id"
}

variable "uri" {
  description = "URI to the route"
}

variable "method" {
  description = "The method in this route"
}

variable "other_methods" {
  description = "Other methods to have this route applied to"
  default = []
}

variable "other_authorizer_ids" {
  description = "List of ids to authorizers to the methods in other_methods variable. If it contains only one, than this one will be applied for all elements of this list"
  default = []
}

variable "authorizer_id" {
  description = "The id to the API authorizer"
  default = null
}

variable "destination_arn" {
  description = "ARN to the route destination (lambda)"
}

variable "destination_name" {
  description = "name of the route destination (lambda)"
}