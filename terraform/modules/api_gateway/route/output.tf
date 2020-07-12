output "resource_id" {
  value = aws_api_gateway_resource.resource.id
}

output "integration_id" {
  value = aws_api_gateway_integration.open_integration.id
}