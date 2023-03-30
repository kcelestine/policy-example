resource "aws_lambda_function" "quizeless_lambda" {
  filename      = "../lambda_output/lambda.zip"
  function_name = "quizeless_lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambdas/quiz_api_lambda.lambda_handler"
  runtime       = "python3.9"
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"
  assume_role_policy = file("lambda-policy.json")
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}
