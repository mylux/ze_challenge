resource "aws_apigatewayv2_api" "api" {
  name          = var.api_name
  protocol_type = var.protocol
  tags = var.tags
}

resource "aws_apigatewayv2_integration" "integration" {
  count = length(var.api_backends)
  api_id = aws_apigatewayv2_api.api.id
  integration_type = "AWS_PROXY"
  integration_method = var.api_backends[count.index].method
  integration_uri = var.api_backends[count.index].target_arn
}

resource "aws_apigatewayv2_route" "route" {
  count = length(var.api_backends)
  api_id = aws_apigatewayv2_api.api.id
  route_key = "${var.api_backends[count.index].method} ${var.api_backends[count.index].uri}"
  target = "integrations/${aws_apigatewayv2_integration.integration[count.index].id}"
}

resource "aws_apigatewayv2_stage" "latest_stage" {
  api_id = aws_apigatewayv2_api.api.id
  name = "latest"
  auto_deploy = true
}

resource "aws_lambda_permission" "invoke_permission_api_gateway" {
  count = length(var.api_backends)
  action = "lambda:InvokeFunction"
  function_name = var.api_backends[count.index].function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${aws_apigatewayv2_api.api.id}/${aws_apigatewayv2_stage.latest_stage.name}/*${var.api_backends[count.index].uri}"
}