resource "aws_iam_role" "role" {
  name = var.name
  assume_role_policy = var.assume_role_policy
}

resource "aws_iam_policy" "policy" {
  count = length(var.policies)
  name = var.policies[count.index].name
  policy = data.aws_iam_policy_document.document[count.index].json
}

resource "aws_iam_role_policy_attachment" "attachment" {
  count = length(var.policies)
  policy_arn = aws_iam_policy.policy[count.index].arn
  role = aws_iam_role.role.name
}