resource "aws_dynamodb_table" "dynamo_table" {
  name           = var.name
  billing_mode   = var.billing_mode
  read_capacity  = var.read_capacity
  write_capacity = var.write_capacity
  hash_key       = element(var.primary_index_attributes, index(var.primary_index_attributes.*.key_type, "hash")).name
  range_key      = contains(var.primary_index_attributes.*.key_type, "range")? lookup(element(var.primary_index_attributes, index(var.primary_index_attributes.*.key_type, "range")),"name", null): null

  dynamic "attribute" {
    for_each = var.primary_index_attributes
    content {
      name = attribute.value.name
      type = attribute.value.type

    }
  }

  dynamic "ttl" {
    for_each = var.ttl_attribute != null? [var.ttl_attribute]: []
    content {
      attribute_name = ttl.value
      enabled = true
    }
  }

  dynamic "local_secondary_index" {
    for_each = var.local_secondary_indices_keys
    content {
      name = local_secondary_index.value.name
      range_key = local_secondary_index.value.range_key
      projection_type = "INCLUDE"
      non_key_attributes = ["msisdn"]
    }
  }

  tags = var.tags
}