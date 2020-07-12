variable "topic_name" {
  description = "Name of the topic"
}

variable "kms_key_id" {
  description = "ID of the key to encrypt data"
  default = "alias/aws/sns"
}