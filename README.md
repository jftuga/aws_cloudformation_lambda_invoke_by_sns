# AWS Cloudformation Lambda invoke by SNS

Use AWS CloudFormation to create a Lambda function that can be invoked via SNS message

## Synopsis

Using `Python 3.9` and `AWS CloudFormation`, create a stack which includes:

* Lambda function that uses:
* * * Environment variables
* * * Tags
* VPC Connectivity from an preexisting VPC *(via a Python script)*
* * Using the default EC2 Security Group
* * Subnets located within the default VPC
* An external `Lambda Layer` hosted on S3
* IAM Policies and Roles to accommodate the Lambda function
* A SNS Topic that is allowed to invoke the Lambda function
* * A SNS Subscription that ties together the SNS Topic and the Lambda function

## Configuration

* Configure the variables in the [config.py](config.py) script, such as `region`, `stack_name`, `aws_profile`, `lambda_folder`, `lambda_code`, etc.
* * Running [lambda-deployment.py](lambda-deployment.py) will substitute the `__SUBNETS__` and `__SECGROUP__` macros in [parameters-template.json](parameters-template.json) with the default EC2 subnet and security group to create `parameters.json`.  This newly created file will be used by the `aws cloudformation create-stack` command as the `--parameters` option.
* Edit the `__LAYERBUCKET__` place holder in [parameters-template.json](parameters-template.json). This will be the S3 bucket location of your `lambda layer`.

## VPC Connectivity

In order to use a preexisting VPC, [vpc_info.py](vpc_info.py) is used to determine the default security groups and subnets.  The `AWS region` is configured in [config.py](config.py).

## Execution

[lambda-deployment.py](lambda-deployment.py) is the main entry point and allows you to create, destroy, and validate a stack as well as upload a lambda layer to S3.

```
usage: lambda-deployment.py [-h] {c,d,v,u}

Execute stack ops, lambda upload

positional arguments:
  {c,d,v,u}   [c]reate the stack; 
              [d]estroy the stack;
              [v]alidate stack files;
              [u]pload lambda zip file to S3 bucket
```

## Operation

**Upload Lambda Layer**

This repo uses a lambda layer which includes the [Paramiko SSH library](https://www.paramiko.org/). 

Here are instructions on [creating aws lambda layers for Python and third party libraries](lambda_layer/README.md).

You will need to first upload the lambda function located in the [lambda_function](lambda_function/) folder using the command below.
It will first create a `zip` file that is then uploaded to S3.

```shell
# upload lambda zip file to S3
python lambda-deployment.py u
```

**Validation**

These third-party programs are used to verify your files before attempting to create a stack.
They must be preinstalled, but can be disabled by modifying the `validate()` function in [lambda-deployment.py](lambda-deployment.py).
* [jsonlint](https://github.com/gosidekick/jsonlint)
* [yamllint](https://github.com/adrienverge/yamllint)
* [cfn-lint](https://github.com/aws-cloudformation/cfn-lint)
* `aws cloudformation validate-template` is also used

```shell
# validate the policy.yml and parameters-template.json files
python lambda-deployment.py v
```

**Create Stack**

This command will generate a `parameters.json` file from [parameters-template.json](parameters-template.json) to use during stack creation. 
It will also use [policy.yml](policy.yml). This can take several minutes to complete.

```shell
# run: aws cloudformation create-stack
python lambda-deployment.py c
```

**Destroy Stack**

This command will destroy the stack once you are finished with your project. This can take several minutes to complete.

```
# run: aws cloudformation delete-stack
python lambda-deployment.py d
```

You can periodically repeat this command to see when the stack has been completely deleted:

```shell
STACKNAME="LambdaInvokedBySNS"
REGION="us-west-2"
aws cloudformation describe-stack-events --region $REGION --stack-name $STACKNAME | \
jq '.StackEvents | .[] | select(.ResourceStatus|test("DELETE_IN_PROGRESS")) | [.LogicalResourceId,.ResourceStatus]'
```

## Checking the lambda function creation status

You can run this command while the stack is being created. It will either return `Pending` or `Active`.
This is usually the most time consuming task during stack creation.
You can periodically repeat this command to see when the function becomes `Active`:

```shell
FUNCNAME="lambda_function"
REGION="us-west-2"
aws lambda get-function-configuration --region $REGION --function-name $FUNCNAME | jq -r ".State"
```

## Testing

[sns_publish](https://github.com/jftuga/sns_publish) can be used to send a message to the SNS topic.
The topic ARN is included in the Cloudformation `Outputs`.

Example:
```shell
sns_publish.exe -s MySubject -m MyMessage -t arn:aws:sns:us-west-2:123456789012:SNSLambdaInvokedBySNS
```

## Future Work

* Possibly add CloudFormation `conditions` for a few of the created resources
* * For example, conditionally create and use `Lambda Layers`
* git pre-commit hooks
* Create a customized `EC2 Security Group` resource instead of relying on the default security group
* Further lock down resources
