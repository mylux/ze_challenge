variable "name" {
  description = "Name of the bucket"
}

variable "acl" {
  description = "Bucket ACL"
  default = "private"
}

variable "index_document" {
  description = "The index document"
  default = "index.html"
}

variable "error_document" {
  description = "The error default document"
  default = "error.html"
}

variable "allowed_methods" {
  description = "Allowed methods"
  type = list(string)
  default = ["GET", "HEAD", "OPTIONS"]
}

variable "cached_methods" {
  description = "Methods that will be cached by Cloudfront"
  type = list(string)
  default = ["GET", "HEAD"]
}

variable "cdn_enabled" {
  description = "Is the distribution enabled of not?"
  default = true
}

variable "viewer_protocol_policy" {
  description = "Viewer Protocol Policy: allow-all, redirect-to-https, https-only"
  default = "allow-all"
}

variable "forward_query_string" {
  description = "Allow Query Strings to be forwarded"
  default = false
}

variable "forward_cookies" {
  description = "Whether to forward cookies or not"
  default = "all"
}