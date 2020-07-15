provider "aws" {
  region = "us-east-2"
}

module "lambda_role" {
  source = "../modules/iam/role"
  name = "zedelivery_test_lambda_role"
  policies = [
    {
      name = "backend_lambdas_full_access_dynamodb_instances"
      statements = [
        {
          actions = [
            "dynamodb:*"
          ]
          resources = [
            module.users_db.table_arn,
            "${module.users_db.table_arn}/index/*",
            module.shops_db.table_arn,
            "${module.shops_db.table_arn}/index/*",
            module.orders_db.table_arn,
            "${module.orders_db.table_arn}/index/*",
            module.couriers_db.table_arn,
            "${module.couriers_db.table_arn}/index/*",
          ]
        }
      ]
    }
  ]

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

module "base_layer" {
  source = "../modules/lambda/layer"
  name = "base"
  package_path = var.base_layer_source_code
  compatible_runtimes = ["python3.8"]
}

module "orders_lambda" {
  source = "../modules/lambda/function"
  handler = "main.main"
  name = "orders"
  runtime = "python3.8"
  source_code_package = var.orders_source_code
  role_arn = module.lambda_role.arn
  role_name = module.lambda_role.name
  layers = [module.base_layer.layer_arn]
}

module "shops_lambda" {
  source = "../modules/lambda/function"
  handler = "main.main"
  name = "shops"
  runtime = "python3.8"
  source_code_package = var.shops_source_code
  role_arn = module.lambda_role.arn
  role_name = module.lambda_role.name
  layers = [module.base_layer.layer_arn]
}

module "couriers_lambda" {
  source = "../modules/lambda/function"
  handler = "main.main"
  name = "couriers"
  runtime = "python3.8"
  source_code_package = var.couriers_source_code
  role_arn = module.lambda_role.arn
  role_name = module.lambda_role.name
  layers = [module.base_layer.layer_arn]
}

module "users_lambda" {
  source = "../modules/lambda/function"
  handler = "main.main"
  name = "users"
  runtime = "python3.8"
  source_code_package = var.users_source_code
  role_arn = module.lambda_role.arn
  role_name = module.lambda_role.name
  layers = [module.base_layer.layer_arn]
}

module "auth_lambda" {
  source = "../modules/lambda/function"
  handler = "main.main"
  name = "auth"
  runtime = "python3.8"
  source_code_package = var.auth_source_code
  role_arn = module.lambda_role.arn
  role_name = module.lambda_role.name
}

module "users_db" {
  source = "../modules/dynamodb"
  primary_index_attributes = var.users_db_keys
  billing_mode = "PROVISIONED"
  name = "users"
  read_capacity = 3
  tags = var.tags
  write_capacity = 3
  global_secondary_indices_keys = [{
    name = "idx_msisdn"
    hash_key = "msisdn"
  }]
}

module "shops_db" {
  source = "../modules/dynamodb"
  primary_index_attributes = var.shops_db_keys
  billing_mode = "PROVISIONED"
  name = "shops"
  read_capacity = 3
  tags = var.tags
  write_capacity = 3
  global_secondary_indices_keys = [{
    name = "idx_username"
    hash_key = "username"
  }]
}

module "couriers_db" {
  source = "../modules/dynamodb"
  primary_index_attributes = var.couriers_db_keys
  billing_mode = "PROVISIONED"
  name = "couriers"
  read_capacity = 3
  tags = var.tags
  write_capacity = 3
  global_secondary_indices_keys = [
    {
      name = "idx_username"
      hash_key = "username"
    }
  ]
}

module "orders_db" {
  source = "../modules/dynamodb"
  primary_index_attributes = var.orders_db_keys
  billing_mode = "PROVISIONED"
  name = "orders"
  read_capacity = 3
  tags = var.tags
  write_capacity = 3
  global_secondary_indices_keys = [
    {
      name = "idx_courier_id"
      hash_key = "courier_id"
    },
    {
      name = "idx_shop_id"
      hash_key = "shop_id"
    },
    {
      name = "idx_user_id"
      hash_key = "user_id"
    }
  ]
  fields_to_copy_to_index = "ALL"
}

module "ze_entrypoint_api" {
  source = "../modules/api_gateway/api"
  api_name = "ze_delivery"
  auth_lambda_name = module.auth_lambda.function_name
  auth_lambda_uri = module.auth_lambda.invoke_arn
  authorizer_name = "ze_entrypoint_authorizer"
  tags = var.tags
  enable_logging = true
  integrations = flatten([
    module.ze_entrypoint_user_create_route.integration_ids,
    module.ze_entrypoint_users_login_route.integration_ids,
    module.ze_entrypoint_users_get_data_route.integration_ids,
    module.ze_entrypoint_couriers_route.integration_ids,
    module.ze_entrypoint_orders_place_list_update_route.integration_ids,
    module.ze_entrypoint_orders_amend_route.integration_ids,
    module.ze_entrypoint_shops_route.integration_ids,
  ])
}

module "ze_entrypoint_user_create_route"{
  source = "../modules/api_gateway/route"
  api_id = module.ze_entrypoint_api.api_id
  destination_arn = module.users_lambda.invoke_arn
  destination_name = module.users_lambda.function_name
  method = "POST"
  other_methods = ["PUT"]
  other_authorizer_ids = [module.ze_entrypoint_api.authorizer_id]
  parent_id = module.ze_entrypoint_api.root_resource_id
  uri = "users"
}

module "ze_entrypoint_users_login_route"{
  source = "../modules/api_gateway/route"
  api_id = module.ze_entrypoint_api.api_id
  destination_arn = module.users_lambda.invoke_arn
  destination_name = module.users_lambda.function_name
  method = "PUT"
  parent_id = module.ze_entrypoint_user_create_route.resource_id
  uri = "login"
}

module "ze_entrypoint_users_get_data_route"{
  source = "../modules/api_gateway/route"
  api_id = module.ze_entrypoint_api.api_id
  destination_arn = module.users_lambda.invoke_arn
  destination_name = module.users_lambda.function_name
  method = "GET"
  uri = "view"
  parent_id = module.ze_entrypoint_user_create_route.resource_id
  authorizer_id = module.ze_entrypoint_api.authorizer_id
}

module "ze_entrypoint_shops_route"{
  source = "../modules/api_gateway/route"
  api_id = module.ze_entrypoint_api.api_id
  destination_arn = module.shops_lambda.invoke_arn
  destination_name = module.shops_lambda.function_name
  method = "POST"
  parent_id = module.ze_entrypoint_api.root_resource_id
  uri = "shops"
  other_methods = ["PUT"]
  other_authorizer_ids = [module.ze_entrypoint_api.authorizer_id]
}

module "ze_entrypoint_shops_login_route"{
  source = "../modules/api_gateway/route"
  api_id = module.ze_entrypoint_api.api_id
  destination_arn = module.shops_lambda.invoke_arn
  destination_name = module.shops_lambda.function_name
  method = "PUT"
  parent_id = module.ze_entrypoint_shops_route.resource_id
  uri = "login"
}

module "ze_entrypoint_shops_get_data_route"{
  source = "../modules/api_gateway/route"
  api_id = module.ze_entrypoint_api.api_id
  destination_arn = module.shops_lambda.invoke_arn
  destination_name = module.shops_lambda.function_name
  method = "GET"
  uri = "view"
  parent_id = module.ze_entrypoint_shops_route.resource_id
  authorizer_id = module.ze_entrypoint_api.authorizer_id
}

module "ze_entrypoint_couriers_route"{
  source = "../modules/api_gateway/route"
  api_id = module.ze_entrypoint_api.api_id
  destination_arn = module.couriers_lambda.invoke_arn
  destination_name = module.couriers_lambda.function_name
  method = "POST"
  parent_id = module.ze_entrypoint_api.root_resource_id
  uri = "couriers"
  other_methods = ["PUT"]
  other_authorizer_ids = [module.ze_entrypoint_api.authorizer_id]
}

module "ze_entrypoint_couriers_login_route"{
  source = "../modules/api_gateway/route"
  api_id = module.ze_entrypoint_api.api_id
  destination_arn = module.couriers_lambda.invoke_arn
  destination_name = module.couriers_lambda.function_name
  method = "PUT"
  parent_id = module.ze_entrypoint_couriers_route.resource_id
  uri = "login"
}

module "ze_entrypoint_couriers_get_data_route"{
  source = "../modules/api_gateway/route"
  api_id = module.ze_entrypoint_api.api_id
  destination_arn = module.couriers_lambda.invoke_arn
  destination_name = module.couriers_lambda.function_name
  method = "GET"
  parent_id = module.ze_entrypoint_couriers_route.resource_id
  uri = "view"
  authorizer_id = module.ze_entrypoint_api.authorizer_id
}

module "ze_entrypoint_orders_place_list_update_route"{
  source = "../modules/api_gateway/route"
  api_id = module.ze_entrypoint_api.api_id
  destination_arn = module.orders_lambda.invoke_arn
  destination_name = module.orders_lambda.function_name
  method = "POST"
  parent_id = module.ze_entrypoint_api.root_resource_id
  uri = "orders"
  authorizer_id = module.ze_entrypoint_api.authorizer_id
  other_methods = ["GET", "PUT"]
  other_authorizer_ids = [module.ze_entrypoint_api.authorizer_id]
}

module "ze_entrypoint_orders_amend_route"{
  source = "../modules/api_gateway/route"
  api_id = module.ze_entrypoint_api.api_id
  destination_arn = module.orders_lambda.invoke_arn
  destination_name = module.orders_lambda.function_name
  method = "PUT"
  parent_id = module.ze_entrypoint_orders_place_list_update_route.resource_id
  uri = "amend"
  authorizer_id = module.ze_entrypoint_api.authorizer_id
}

//module "site_s3" {
//  source = "../modules/static_site/"
//  name = "test-lux-zedelivery"
//}