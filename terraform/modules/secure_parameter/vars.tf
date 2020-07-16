variable "name" {
  description = "The parameter name"
}

variable "value" {
  description = "The parameter value"
}

variable "tags" {
  type = map(string)
  description = "AWS Tags"
}