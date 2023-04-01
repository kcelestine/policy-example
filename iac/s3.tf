resource "aws_s3_bucket" "quiz_bucket" {
  bucket = var.bucket_name_site
}

resource "aws_s3_bucket" "quiz_bucket_data" {
  bucket = var.bucket_name_data
}

resource "aws_s3_bucket_website_configuration" "quiz_bucket_config" {
  bucket = aws_s3_bucket.quiz_bucket.bucket
  index_document {
    suffix = "index.html"
  }
}

# I need the website URL as an endpoint I can use in browser
output "website_url" {
  value = "http://${aws_s3_bucket_website_configuration.quiz_bucket_config.website_endpoint}"
}

resource "aws_s3_bucket_policy" "quiz_bucket_policy" {
  bucket = aws_s3_bucket.quiz_bucket.id
  policy = templatefile("s3-policy.json", { bucket = var.bucket_name_site })
}

locals {
  server_js_file_path = "${path.module}/../storage/website/js/server.js"
  new_quiz_api_uri    = replace(
    "${aws_api_gateway_deployment.quizless_api_deployment.invoke_url}/quiz",
    "/",
    "\\/"
  )
}

# modify the file "server.js" to substitute the file's content (URI)
resource "null_resource" "modify_server_js_file" {
  triggers = {
    file_contents = md5(file(local.server_js_file_path))
  }
  provisioner "local-exec" {
    command = "sed -i 's/TEMPLATE_BASE_URL/${local.new_quiz_api_uri}/g' ${local.server_js_file_path}"
  }
  depends_on = [aws_api_gateway_deployment.quizless_api_deployment]
}

module "template_files_website" {
  source = "hashicorp/dir/template"
  base_dir = "${path.module}/../storage/website"
  depends_on   = [null_resource.modify_server_js_file]
}

resource "aws_s3_object" "quiz_bucket_site_files" {
  for_each     = module.template_files_website.files
  bucket       = aws_s3_bucket.quiz_bucket.id
  key          = each.key
  content_type = each.value.content_type
  source       = each.value.source_path
  content      = each.value.content
  etag         = each.value.digests.md5
}

# modify the file "server.js" back to it's original state
resource "null_resource" "modify_server_js_file_back" {
  triggers = {
    always_run = "${timestamp()}"
  }
  provisioner "local-exec" {
    command = <<EOT
      sed -i 's/^this\.baseUrl =.*;/this.baseUrl = "TEMPLATE_BASE_URL";/' ${local.server_js_file_path}
    EOT
  }
  depends_on = [aws_s3_object.quiz_bucket_site_files]
}

module "template_files_data" {
  source = "hashicorp/dir/template"
  base_dir = "${path.module}/../storage/quiz"
}

resource "aws_s3_object" "quiz_bucket_data_files" {
  for_each     = module.template_files_data.files
  bucket       = aws_s3_bucket.quiz_bucket_data.id
  key          = each.key
  content_type = each.value.content_type
  source       = each.value.source_path
  content      = each.value.content
  etag         = each.value.digests.md5
}
