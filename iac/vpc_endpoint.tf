resource "aws_vpc_endpoint" "quizless_vpc_endpoint" {
  vpc_id            = aws_vpc.quizless_vpc.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [
    aws_route_table.quizless_route_table.id
  ]
}
