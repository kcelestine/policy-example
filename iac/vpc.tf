resource "aws_vpc" "quizless_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "quizless-vpc"
  }
  enable_dns_support   = true
  enable_dns_hostnames = true
}

# create a route table for the VPC
resource "aws_route_table" "quizless_route_table" {
  vpc_id = aws_vpc.quizless_vpc.id
  tags = {
    Name = "quizless-route-table"
  }
}

# create a private subnet where both Lambda and Redis cluster reside
resource "aws_subnet" "quizless_private_subnet" {
  vpc_id = aws_vpc.quizless_vpc.id
  cidr_block = var.quizless_subnet_cidr
  availability_zone = "eu-central-1a"
  tags = {
    Name = "quizless-private-subnet"
  }
}

# assign the route table the subnet
resource "aws_route_table_association" "quizless_association" {
  subnet_id      = aws_subnet.quizless_private_subnet.id
  route_table_id = aws_route_table.quizless_route_table.id
}