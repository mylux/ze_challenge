resource "aws_cloudfront_distribution" "cloudfront" {
  enabled = var.enabled
  default_cache_behavior {
    allowed_methods = var.allowed_methods
    cached_methods = var.cached_methods
    target_origin_id = ""
    viewer_protocol_policy = ""
    forwarded_values {
      query_string = false
      cookies {
        forward = var.
      }
    }
  }
  origin {
    domain_name = ""
    origin_id = ""
  }
  restrictions {
    geo_restriction {
      restriction_type = ""
    }
  }
  viewer_certificate {}
}