terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region  = "eu-central-1"
  profile = "quizless"
}

resource "aws_s3_bucket" "quiz_bucket" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_website_configuration" "quiz_bucket_config" {
  bucket = aws_s3_bucket.quiz_bucket.bucket
  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_policy" "quiz_bucket_policy" {
  bucket = aws_s3_bucket.quiz_bucket.id
  policy = templatefile("s3-policy.json", { bucket = var.bucket_name })
}

module "template_files" {
  source = "hashicorp/dir/template"

  base_dir = "${path.module}/../storage/website"
}

resource "aws_s3_object" "quiz_bucket_site_files" {
  for_each     = module.template_files.files
  bucket       = aws_s3_bucket.quiz_bucket.id
  key          = each.key
  content_type = each.value.content_type
  source       = each.value.source_path
  content      = each.value.content
  etag         = each.value.digests.md5
}
