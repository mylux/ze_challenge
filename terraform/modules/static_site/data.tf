data "template_file" "s3_policy" {
  template = file("${path.module}/files/s3_policy.json")
  vars = {
    bucket_name = var.name
    origin_access_id = aws_cloudfront_origin_access_identity.origin_access_identity.id
  }
}