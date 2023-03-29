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

resource "aws_s3_bucket" "storage" {
  bucket = "storage"
  acl    = "public-read"
  tags   = {
    role = "quiz-bucket"
  }
  website {
    index_document = "index.html"
  }
}

resource "aws_s3_bucket_object" "storage" {
  for_each = fileset("${path.module}/../storage", "**/*")

  bucket = aws_s3_bucket.storage.id
  key    = each.value
  source = "${path.module}/../storage/${each.value}"
}