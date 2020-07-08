resource "aws_lambda_function" "function" {
  filename      = var.source_code_package
  function_name = var.name
  role          = var.role_arn
  handler       = var.handler

  source_code_hash = filebase64sha256(var.source_code_package)

  runtime = var.runtime

  dynamic "environment" {
    for_each = length(var.environment_vars) > 0?[var.environment_vars]:[]
    content {
      variables = environment.value
    }
  }
}

resource "aws_iam_role_policy_attachment" "attach_lambda_basic_execution_role" {
  role       = var.role_name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}