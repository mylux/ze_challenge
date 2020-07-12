resource "aws_sns_topic" "sns" {
  name              = var.topic_name
  kms_master_key_id = var.kms_key_id
}