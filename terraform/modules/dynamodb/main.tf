resource "aws_dynamodb_table" "dynamo_table" {
  name           = var.name
  billing_mode   = var.billing_mode
  read_capacity  = var.read_capacity
  write_capacity = var.write_capacity
  hash_key       = element(var.attributes, index(var.attributes.*.key_type, "hash")).name
  range_key      = contains(var.attributes.*.key_type, "range")? lookup(element(var.attributes, index(var.attributes.*.key_type, "range")),"name", null): null

  dynamic "attribute" {
    for_each = var.attributes
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

  tags = var.tags
}