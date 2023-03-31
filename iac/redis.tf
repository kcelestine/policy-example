resource "aws_elasticache_cluster" "quiz_cluster" {
  cluster_id           = "quiz-cluster"
  engine               = "redis"
  node_type            = "cache.t2.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis3.2"
  engine_version       = "3.2.10"
  port                 = 6379

  subnet_group_name    = aws_elasticache_subnet_group.elasticache_subnet_group.name
  security_group_ids   = [aws_security_group.quizless_redis_security_group.id]
}

resource "aws_elasticache_subnet_group" "elasticache_subnet_group" {
  name       = "elasticache-subnet-group"
  subnet_ids = [aws_subnet.quizless_private_subnet.id]
}

# security group to allow limited ingress access to VPC
# and unlimited egress traffic
resource "aws_security_group" "quizless_redis_security_group" {
  vpc_id       = aws_vpc.quizless_vpc.id
  name         = "Quizless Redis security group"
  description  = "Ingress is limited, egress is unlimited"

  # allow ingress of port 6379 for Redis from API Gateway
  ingress {
    cidr_blocks = [var.quizless_redis_ingress_cidr]
    from_port   = 6379
    to_port     = 6379
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
    Name = "Quizless Redis Security Group"
  }
}