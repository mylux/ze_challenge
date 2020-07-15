resource "aws_api_gateway_resource" "resource" {
  parent_id = var.parent_id
  path_part = var.uri
  rest_api_id = var.api_id
}

resource "aws_api_gateway_method" "method" {
  authorization = var.authorizer_id == null? "NONE": "CUSTOM"
  authorizer_id = var.authorizer_id
  http_method = var.method
  resource_id = aws_api_gateway_resource.resource.id
  rest_api_id = var.api_id
}

resource "aws_api_gateway_method" "other_methods" {
  count = length(var.other_methods)
  authorization = var.other_authorizer_ids == []? "NONE": "CUSTOM"
  authorizer_id = length(var.other_authorizer_ids) == 1? var.other_authorizer_ids[0]: length(var.other_authorizer_ids) == 0? null : var.other_authorizer_ids[count.index]
  http_method = var.other_methods[count.index]
  resource_id = aws_api_gateway_resource.resource.id
  rest_api_id = var.api_id
}


resource "aws_api_gateway_integration" "integration" {
  count = length(flatten([aws_api_gateway_method.method, aws_api_gateway_method.other_methods]))
  http_method = flatten([aws_api_gateway_method.method, aws_api_gateway_method.other_methods])[count.index].http_method
  resource_id = aws_api_gateway_resource.resource.id
  rest_api_id = var.api_id
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = var.destination_arn
}

resource "aws_lambda_permission" "invoke_permission_api_gateway_method" {
  action = "lambda:InvokeFunction"
  function_name = var.destination_name
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${var.api_id}/*/${var.method}${aws_api_gateway_resource.resource.path}"
}

resource "aws_lambda_permission" "invoke_permission_api_gateway_other_methods" {
  count = length(var.other_methods)
  action = "lambda:InvokeFunction"
  function_name = var.destination_name
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${var.api_id}/*/${var.other_methods[count.index]}${aws_api_gateway_resource.resource.path}"
}
