variable "api_name" {
  description = "Name of the API"
}

variable "protocol" {
  default = "HTTP"
  description = "Protocol of this API"
}

variable "api_backends" {
  description = "List of routes to be added to the API"
  type = list(object({
    method = string
    target_arn = string
    uri = string
    function_name = string
  }))
}

variable "tags" {
  description = "Tags to add to the resources"
  type = map(string)
}