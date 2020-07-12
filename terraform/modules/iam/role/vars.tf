variable "name" {
  description = "Name of the role"
}

variable "assume_role_policy" {
  description = "The policy content"
}

variable "policies" {
  description = "The policies to attach to a role"
  type = list(
    object({
      name = string
      statements = list(
        object({
          actions = list(string)
          resources = list(string)
        })
      )
    })
  )
  default = []
}