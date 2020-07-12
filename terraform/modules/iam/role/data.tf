data "aws_iam_policy_document" "document" {
  count = length(var.policies)

  dynamic "statement"{

    for_each = var.policies[count.index].statements
    content {
      sid = statement.key
      actions = statement.value.actions
      resources = statement.value.resources
    }
  }
}