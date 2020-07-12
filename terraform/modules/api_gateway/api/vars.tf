variable "api_name" {
  description = "Name of the API"
}

variable "tags" {
  description = "Tags to add to the resources"
  type = map(string)
}

variable "authorizer_name" {
  description = "Name of the authorized in API Gateway"
}

variable "auth_lambda_uri" {
  description = "URI to the authentication/authorization lambda"
}

variable "auth_lambda_name" {
  description = "Name of the authentication/authorization lambda"
}

variable "stage_name" {
  description = "Name to be giver a stage"
  default = "production"
}

variable "enable_logging" {
  description = "Whether to enable or not logging to cloudwatch"
  default = false
}

variable "log_retention_days" {
  description = "Time to maintain logs in Cloudwatch"
  default = 1
}

variable "log_format" {
  description = "Cloudwatch api log format"
  default = "$context.identity.sourceIp $context.identity.caller  $context.identity.user [$context.requestTime] \"$context.httpMethod $context.resourcePath $context.protocol\" $context.status $context.responseLength $context.requestId $context.integrationErrorMessage"
}

variable "api_log_cloudwatch_policy_name" {
  description = "Name to give to the policy that allows the api write logs to cloudwatch"
  default = "api_log_cloudwatch_policy"
}

variable "api_log_cloudwatch_role_name" {
  description = "Name to give to the role containing the policy that allows the api write logs to cloudwatch"
  default = "api_gateway_cloudwatch_role"
}

variable "integrations" {
  description = "Integration"
}