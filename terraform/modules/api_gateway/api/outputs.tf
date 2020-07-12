output "api_endpoint" {
  value = aws_api_gateway_stage.stage.invoke_url
}

output "api_id" {
  value = aws_api_gateway_rest_api.api.id
}

output "root_resource_id" {
  value = aws_api_gateway_rest_api.api.root_resource_id
}

output "authorizer_id" {
  value = aws_api_gateway_authorizer.auth.id
}