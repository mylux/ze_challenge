resource "aws_s3_bucket" "bucket" {
  bucket = var.name
  acl    = var.acl
  policy = data.template_file.s3_policy.rendered

  website {
    index_document = var.index_document
    error_document = var.error_document
  }
}

locals {
  s3_origin_id = "zeDeliveryStaticSite"
}

resource "aws_cloudfront_origin_access_identity" "origin_access_identity" {
  comment = "Origin Access Identity from CLoudFront to s3"
}

resource "aws_cloudfront_distribution" "cloudfront" {
  enabled = var.cdn_enabled
  default_cache_behavior {
    allowed_methods = var.allowed_methods
    cached_methods = var.cached_methods
    target_origin_id = local.s3_origin_id
    viewer_protocol_policy = var.viewer_protocol_policy
    forwarded_values {
      query_string = var.forward_query_string
      cookies {
        forward = var.forward_cookies
      }
    }
  }
  origin {
    domain_name = aws_s3_bucket.bucket.bucket_regional_domain_name
    origin_id = local.s3_origin_id

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.origin_access_identity.cloudfront_access_identity_path
    }

  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}