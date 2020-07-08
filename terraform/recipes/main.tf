provider "aws" {
  region = "us-east-2"
}

module "lambda_role" {
  source = "../modules/iam/role"
  name = "zedelivery_test_lambda_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


module "orders_lambda" {
  source = "../modules/lambda"
  handler = "main.main"
  name = "orders"
  runtime = "python3.8"
  source_code_package = var.orders_source_code
  role_arn = module.lambda_role.arn
  role_name = module.lambda_role.name
}

module "shops_lambda" {
  source = "../modules/lambda"
  handler = "main.main"
  name = "shops"
  runtime = "python3.8"
  source_code_package = var.shops_source_code
  role_arn = module.lambda_role.arn
  role_name = module.lambda_role.name
}

module "couriers_lambda" {
  source = "../modules/lambda"
  handler = "main.main"
  name = "couriers"
  runtime = "python3.8"
  source_code_package = var.couriers_source_code
  role_arn = module.lambda_role.arn
  role_name = module.lambda_role.name
}

module "users_lambda" {
  source = "../modules/lambda"
  handler = "main.main"
  name = "users"
  runtime = "python3.8"
  source_code_package = var.users_source_code
  role_arn = module.lambda_role.arn
  role_name = module.lambda_role.name
}

module "users_db" {
  source = "../modules/dynamodb"
  attributes = var.users_db_keys
  billing_mode = "PROVISIONED"
  name = "users"
  read_capacity = 3
  tags = var.tags
  write_capacity = 3
}

module "shops_db" {
  source = "../modules/dynamodb"
  attributes = var.shops_db_keys
  billing_mode = "PROVISIONED"
  name = "shops"
  read_capacity = 3
  tags = var.tags
  write_capacity = 3
}

module "couriers_db" {
  source = "../modules/dynamodb"
  attributes = var.couriers_db_keys
  billing_mode = "PROVISIONED"
  name = "couriers"
  read_capacity = 3
  tags = var.tags
  write_capacity = 3
}

module "orders_db" {
  source = "../modules/dynamodb"
  attributes = var.orders_db_keys
  billing_mode = "PROVISIONED"
  name = "orders"
  read_capacity = 3
  tags = var.tags
  write_capacity = 3
}

module "ze_entry" {
  source = "../modules/api_gateway"
  api_backends = [
    {
      method = "POST"
      uri = "/users"
      target_arn = module.users_lambda.invoke_arn
      function_name = module.users_lambda.function_name
    },
    {
      method = "POST"
      uri = "/orders"
      target_arn = module.orders_lambda.invoke_arn
      function_name = module.orders_lambda.function_name
    },
    {
      method = "POST"
      uri = "/couriers"
      target_arn = module.couriers_lambda.invoke_arn
      function_name = module.couriers_lambda.function_name
    },
    {
      method = "POST"
      uri = "/shops"
      target_arn = module.shops_lambda.invoke_arn
      function_name = module.shops_lambda.function_name
    }
  ]
  api_name = "ze_delivery"
  tags = var.tags
}

module "site_s3" {
  source = "../modules/static_site/"
  name = "test-lux-zedelivery"
}