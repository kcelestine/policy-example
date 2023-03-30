resource "aws_lambda_function" "quizeless_lambda" {
  filename      = "../lambda_output/lambda.zip"
  function_name = "quizeless_lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambdas/quiz_api_lambda.lambda_handler"
  runtime       = "python3.9"

  environment {
    variables = {
      STORAGE_URI = "quizless-bucket-data"
      STORAGE_TYPE = "S3"
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "lambda_role"
  assume_role_policy = file("lambda-assume-role-policy.json")
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "lambda-s3-policy"
  description = "A policy enabling the lambda reading S3 bucket"
  policy      = templatefile("lambda-access-s3-policy.json", { bucket_id = aws_s3_bucket.quiz_bucket_data.id })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "${aws_iam_policy.lambda_s3_policy.arn}"
}
