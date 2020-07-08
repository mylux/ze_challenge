variable "allowed_methods" {
  description = "Allowed methods"
  type = list(string)
  default = ["GET", "HEAD", "OPTIONS"]
}

variable "cached_methods" {
  description = "Methods that will be cached by Cloudfront"
  type = list(string)
  default = ["GET"]
}

variable "enabled" {
  description = "Is the distribution enabled of not?"
  default = true
}