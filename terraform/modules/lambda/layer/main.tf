resource "aws_lambda_layer_version" "layer" {
  layer_name = var.name
  filename = var.package_path
  source_code_hash = filebase64sha256(var.package_path)
  compatible_runtimes = var.compatible_runtimes
}