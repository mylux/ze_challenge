resource "aws_ssm_parameter" "parameter" {
  name  = var.name
  type  = "SecureString"
  value = var.value
  tags = var.tags
}
