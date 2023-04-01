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

Check the deployed website here:
http://quizless-bucket.s3-website.eu-central-1.amazonaws.com/

# Downgrade Python to 3.9
```shell
rm -rf venv
pyenv which python3.9
$(pyenv which python3.9) -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Might require this line:
```shell
pip uninstall dataclasses
```

Update the Lambda (only) if necessary:
```shell
terraform apply -replace=aws_lambda_function.quizeless_lambda --auto-approve
```

Check the "quizless-lambda" with the payload:
```json
{
  "requested_operation": "quiz-topics",
  "payload": {}
}
```

or this payload to check both S3 and ElastiCache accessibility:
```json
{
  "requested_operation": "quiz-start",
  "payload": {"topic_id": "d729af45-5ed3-42d0-ac57-d4485b64b067", "user_name": "Alph"}
}
```

Provide this .env file for local testing:
```shell
AWS_ACCESS_KEY_ID=A....A
AWS_SECRET_ACCESS_KEY=B........6
AWS_DEFAULT_REGION=eu-central-1
STORAGE_URI=quizless-bucket-data
STORAGE_TYPE=S3
```

Now test the deployed API:
```shell
curl -iX "POST" "https://dvt15laxzl.execute-api.eu-central-1.amazonaws.com/prod/quiz" \
  -H "Content-Type: application/json" \
  -d '{"requested_operation": "quiz-start", "payload":{"topic_id": "d729af45-5ed3-42d0-ac57-d4485b64b067", "user_name": "Alph"}}'
```