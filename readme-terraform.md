# Install Terraform 
Install Terraform following the instruction on the official website:
[https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli).

# Create an AWS user
1) Go to IAM
2) Create a user and add this user to the "administrators" group with `AdministratorAccess` attached policy
3) On the user's page go to "Security credentials" tab, scroll down to "Access keys" and an create access key. 

# Enable Terraform access to AWS
Edit the file `~/.aws/credentials` and add the following lines there:
```shell
[quizless]
aws_access_key_id=AKIA45CZI2Z4CB74SART
aws_secret_access_key=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
```

then configure the AWS Terraform provider in `main.tf`:
```yaml
provider "aws" {
  region  = "eu-central-1"
  profile = "quizless"  # add this line
}
```

Now we're able, for instance, to spin up an ECS cluster:
```yaml
resource "aws_elasticache_cluster" "quiz_cluster" {
  cluster_id           = "quiz-cluster"
  engine               = "redis"
  node_type            = "cache.t2.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis3.2"
  engine_version       = "3.2.10"
  port                 = 6379
}
```

Don't forget to properly set up `.gitignore`.