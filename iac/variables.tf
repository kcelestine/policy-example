variable "region" {
  default = "eu-central-1"
  type    = string
}

variable "bucket_name_site" {
  default = "quizless-bucket"
  type    = string
}

variable "bucket_name_data" {
  default = "quizless-bucket-data"
  type    = string
}

variable "quizless_subnet_cidr" {
  default = "10.0.1.0/24"
  type    = string
}

variable "quizless_lambda_ingress_cidr" {
  default = "10.0.1.0/24"
  type    = string
}

variable "quizless_redis_ingress_cidr" {
  default = "10.0.1.0/24"
  type    = string
}