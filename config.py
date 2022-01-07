
# the CF stack name
stack_name = "LambdaInvokedBySNS"

# used by both create and destroy
region = "Your-AWS-Region"

# A IAM user with admin access
aws_profile = "default"

# the main CF definition file
template = "policy.yml"

# Parameter file containing macros and placeholders
parameters_template = "parameters-template.json"

# macros have been substituted in this generated file
# it gets destroyed and recreated each time "lambda-deployment.py c" is executed
parameters = "parameters.json"

# used by the "lambda-deployment.py u" command
lambda_folder = "lambda_function"
lambda_code = "*.py"
lambda_layer_folder = "lambda_layer"
