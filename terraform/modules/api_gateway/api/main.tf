resource "aws_api_gateway_rest_api" "api" {
  depends_on = [aws_api_gateway_account.account]
  name        = var.api_name
  description = "${var.api_name} API"
  tags = var.tags
}

locals {
  md5_file = filemd5("${path.module}/main.tf")
}

resource "aws_api_gateway_authorizer" "auth" {
  name                   = var.authorizer_name
  rest_api_id            = aws_api_gateway_rest_api.api.id
  authorizer_uri         = var.auth_lambda_uri
  authorizer_result_ttl_in_seconds = 0
}

resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_description = "Deployment meta data: ${local.md5_file}"
  depends_on = [var.integrations]
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "stage" {
  stage_name    = var.stage_name
  rest_api_id   = aws_api_gateway_rest_api.api.id
  deployment_id = aws_api_gateway_deployment.deployment.id

  dynamic "access_log_settings" {
    for_each = var.enable_logging? [var.log_format] : []
    content {

      destination_arn = aws_cloudwatch_log_group.api_logging.arn
      format = access_log_settings.value
    }
  }
}

resource "aws_cloudwatch_log_group" "api_logging" {
  name              = "api_gateway_access_logs_${aws_api_gateway_rest_api.api.id}/${var.stage_name}"
  retention_in_days = var.log_retention_days
  tags = var.tags
}

resource "aws_api_gateway_account" "account" {
  cloudwatch_role_arn = aws_iam_role.cloudwatch_logs_role.arn
}

resource "aws_iam_role" "cloudwatch_logs_role" {
  name = var.api_log_cloudwatch_role_name
  tags = var.tags

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "cloudwatch_policy" {
  name = var.api_log_cloudwatch_policy_name
  role = aws_iam_role.cloudwatch_logs_role.id

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents",
                "logs:GetLogEvents",
                "logs:FilterLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_lambda_permission" "invoke_permission_auth_lambda" {
  action = "lambda:InvokeFunction"
  function_name = var.auth_lambda_name
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/authorizers/${aws_api_gateway_authorizer.auth.id}"
}