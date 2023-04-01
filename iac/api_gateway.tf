resource "aws_api_gateway_rest_api" "quizless_api" {
  name = "quizless-api"
}

resource "aws_api_gateway_resource" "quiz_resource" {
  rest_api_id = aws_api_gateway_rest_api.quizless_api.id
  parent_id   = aws_api_gateway_rest_api.quizless_api.root_resource_id
  path_part   = "quiz"
}

module "api-gateway-enable-cors" {
    source  = "squidfunk/api-gateway-enable-cors/aws"
    version = "0.3.3"
    api_id          = aws_api_gateway_rest_api.quizless_api.id
    api_resource_id = aws_api_gateway_resource.quiz_resource.id
}

resource "aws_api_gateway_method" "quiz_command_method" {
  rest_api_id   = aws_api_gateway_rest_api.quizless_api.id
  resource_id   = aws_api_gateway_resource.quiz_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "quiz_api_integration" {
  rest_api_id             = aws_api_gateway_rest_api.quizless_api.id
  resource_id             = aws_api_gateway_resource.quiz_resource.id
  http_method             = aws_api_gateway_method.quiz_command_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.quizeless_lambda.invoke_arn
}

resource "aws_lambda_permission" "allow-api-gateway" {
  function_name = "${aws_lambda_function.quizeless_lambda.function_name}"
  statement_id  = "AllowExecutionFromApiGateway"
  action        = "lambda:InvokeFunction"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.quizless_api.execution_arn}/*/*/*"
  # depends_on    = ["aws_api_gateway_rest_api.quizless_api"]
}

# https://stackoverflow.com/questions/61027859/conflictexception-stage-already-exist-from-aws-api-gateway-deployment-with-stag
# Dummy API Deployment
resource "aws_api_gateway_deployment" "dummy" {
  rest_api_id = "${aws_api_gateway_rest_api.quizless_api.id}"
  stage_description = "Deployment at ${timestamp()}"
  lifecycle {
    create_before_destroy = true
  }
  depends_on = [
    aws_api_gateway_integration.quiz_api_integration
  ]
}

# Create a stage refering to the dummy.
# The 2nd/true deployment will later refer to this stage
resource "aws_api_gateway_stage" "quizless_api_dummy_stage" {
  stage_name    = "prod"
  rest_api_id   = aws_api_gateway_rest_api.quizless_api.id
  deployment_id = aws_api_gateway_deployment.dummy.id

  # xray_tracing_enabled = var.apigw_xray_tracing_enabled

  tags = {
    Environment = "prod"
  }

  depends_on = [
    aws_api_gateway_deployment.dummy
  ]
}

#--------------------------------------------------------------------------------
# Legitimate API Deployment
#--------------------------------------------------------------------------------
resource "aws_api_gateway_deployment" "quizless_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.quizless_api.id
  stage_name  = aws_api_gateway_stage.quizless_api_dummy_stage.stage_name

  lifecycle {
    create_before_destroy = true
  }
}

output "api_endpoint" {
  value = aws_api_gateway_deployment.quizless_api_deployment.invoke_url
}