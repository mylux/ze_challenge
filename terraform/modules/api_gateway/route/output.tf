output "resource_id" {
  value = aws_api_gateway_resource.resource.id
}

output "integration_ids" {
  value = aws_api_gateway_integration.integration.*.id
}