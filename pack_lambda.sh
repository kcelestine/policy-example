#!/bin/bash

rm -rf lambda_src
mkdir lambda_src
# cp requirements.txt lambda_src
cp -a src/. lambda_src
pip install --target lambda_src -r requirements.txt
# cp -r venv/lib/python3.9/site-packages/. lambda_src
rm lambda_output/lambda.zip
# cd lambda_src && zip -r ../lambda_output/lambda.zip . -x "tests/*" -x ".pytest_cache/*" -x "__pycache__/*"
cd lambda_src && zip -r ../lambda_output/lambda.zip .