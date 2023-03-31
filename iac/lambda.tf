resource "aws_lambda_function" "quizeless_lambda" {
  filename      = "../lambda_output/lambda.zip"
  function_name = "quizeless_lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambdas/quiz_api_lambda.lambda_handler"
  runtime       = "python3.9"

  environment {
    variables = {
      STORAGE_URI  = "quizless-bucket-data"
      STORAGE_TYPE = "S3"
      REDIS_HOST   = aws_elasticache_cluster.quiz_cluster.cache_nodes[0].address
    }
  }

  vpc_config {
    subnet_ids         = [aws_subnet.quizless_private_subnet.id]
    security_group_ids = [aws_security_group.quizless_lambda_security_group.id]
  }
}

# add policies enabling both S3 and ElastiCache resource usage
resource "aws_iam_role" "lambda_role" {
  name               = "lambda_role"
  assume_role_policy = file("lambda-assume-role-policy.json")
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "lambda-s3-policy"
  description = "A policy enabling the lambda reading S3 bucket"
  policy      = templatefile("lambda-access-s3-policy.json", { bucket_id = aws_s3_bucket.quiz_bucket_data.id })
}

resource "aws_iam_policy" "lambda_redis_policy" {
  name        = "lambda-redis-policy"
  description = "A policy enabling the lambda working with the ElastiCache Redis"
  policy      = templatefile("lambda-access-redis-policy.json", { redis_id = aws_elasticache_cluster.quiz_cluster.id })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "${aws_iam_policy.lambda_s3_policy.arn}"
}

resource "aws_iam_role_policy_attachment" "lambda_redis_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "${aws_iam_policy.lambda_redis_policy.arn}"
}

resource "aws_iam_policy" "lambda_network_policy" {
  name        = "lambda-network-policy"
  description = "A policy enabling the lambda calling CreateNetworkInterface"
  policy      = file("lambda-network-policy.json")
}

resource "aws_iam_role_policy_attachment" "lambda_network_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "${aws_iam_policy.lambda_network_policy.arn}"
}

# security group to allow limited ingress access to VPC
# and unlimited egress traffic
resource "aws_security_group" "quizless_lambda_security_group" {
  vpc_id       = aws_vpc.quizless_vpc.id
  name         = "Quizless Lambda security group"
  description  = "Ingress is limited, egress is unlimited"

  # allow ingress of port 80 for Lambda from API Gateway
  ingress {
    cidr_blocks = [var.quizless_lambda_ingress_cidr]
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
  }

  # allow egress of all ports
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "Quizless Lambda Security Group"
  }
}