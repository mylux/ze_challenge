variable "runtime" {
  description = "Runtime of the lambda (python, node, java, etc)"
}

variable "source_code_package" {
  description = "Zip file containing lambda source code"
}

variable "name" {
  description = "Name of the function"
}

variable "handler" {
  description = "Handler (main function) of the lambda"
}

variable "environment_vars" {
  type = map(string)
  default = {}
}

variable "role_arn" {
  description = "Lambda execution role ARN"
}

variable "role_name" {
  description = "Lambda execution role Name"
}