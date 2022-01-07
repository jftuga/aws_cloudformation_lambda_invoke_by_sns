
# used by both create and destroy
region = "us-west-2"
stack_name = "LambdaInvokedBySNS"
aws_profile = "cfn-admin"
template = "policy.yml"
parameters_template = "parameters-template.json"

# this file gets destroyed and recreated each time
parameters = "parameters.json"

# used by update-lambda
lambda_folder = "lambda_function"
lambda_code = "*.py"
lambda_layer_folder = "lambda_layer"
