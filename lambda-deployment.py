r"""
deployment.py
-John Taylor
2021-12-29

This is the controlling entry point for stack operations. It is a wrapper for these commands:

v:  validate the template and parameters files
c:  aws cloudformation create-stack
d:  aws cloudformation delete-stack
u:  upload lambda layer via: aws s3 cp
"""

import argparse
import glob
import json
import os.path
import subprocess
import sys
import zipfile
from vpc_info import VpcInfo
from config import region, stack_name, aws_profile, template, parameters_template, parameters, lambda_folder, \
    lambda_code, lambda_layer_folder


def create(group_name: str = "default"):
    vpc_info = VpcInfo(f"{region}")
    raw_subnets = vpc_info.get_subnets()
    subnets = ",".join(raw_subnets)
    sec_group = vpc_info.get_security_group_from_name(group_name)
    if not sec_group:
        print(f"No security group id found for {group_name}")
    print(f"{subnets=}")
    print(f"{sec_group=}")

    with open(parameters_template) as fp:
        contents = fp.read()
    contents = contents.replace("__SUBNETS__", subnets).replace("__SECGROUP__", sec_group)
    with open(parameters, mode="w") as fp:
        fp.write(contents)
    print(f"Created file: {parameters}")
    print()

    cmd = f"aws cloudformation create-stack --stack-name {stack_name} --profile {aws_profile} --template-body file://{template} --capabilities CAPABILITY_NAMED_IAM --parameters file://{parameters} --region {region}"
    execute_command(cmd)


def destroy():
    cmd = f"aws cloudformation delete-stack --stack-name {stack_name} --profile {aws_profile} --region {region}"
    execute_command(cmd)


def upload():
    zip_filename = create_zipfile()
    bucket = get_bucket()
    cmd = f"aws s3 cp {zip_filename} s3://{bucket}/"
    if not os.path.exists(zip_filename):
        print(f"file not found: {zip_filename}", file=sys.stderr)
        sys.exit(1)
    execute_command(cmd)

    cmd = f"aws s3 sync {lambda_layer_folder} s3://{bucket}/"
    if not os.path.exists(lambda_layer_folder):
        print(f"directory not found: {lambda_layer_folder}", file=sys.stderr)
        sys.exit(1)
    execute_command(cmd)


def validate():
    # https://github.com/gosidekick/jsonlint
    want_jl = True
    if want_jl:
        cmd = f"jl -i {parameters_template}"
        execute_command(cmd, show_output=False)

    # https://github.com/adrienverge/yamllint
    want_yaml_lint = True
    if want_yaml_lint:
        cmd = f"yamllint -f colored -s {template}"
        execute_command(cmd)

    # https://github.com/aws-cloudformation/cfn-lint
    want_cfn_lint = True
    if want_cfn_lint:
        cmd = f"cfn-lint -i W2001 -t {template}"
        execute_command(cmd)

    # https://docs.aws.amazon.com/cli/latest/reference/cloudformation/validate-template.html
    cmd = f"aws cloudformation validate-template --no-cli-pager --template-body file://{template}"
    execute_command(cmd, show_output=False)


def create_zipfile() -> str:
    zip_filename = f"{lambda_folder}.zip"
    print(zip_filename)
    zf = zipfile.ZipFile(zip_filename, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9)
    code_path = os.path.join(lambda_folder, lambda_code)
    all_files = glob.glob(code_path)
    # print(f"{code_path=}")
    # print(f"{all_files=}")
    with zf as archive:
        for f in all_files:
            archive.write(f, os.path.basename(f))
    return zip_filename


def get_bucket() -> str:
    bucket = None
    with open(parameters_template) as fp:
        json_data = json.load(fp)

    for keyval in json_data:
        if "ParameterKey" in keyval and keyval["ParameterKey"] == "LambdaLayerBucketNameKeyName":
            bucket = keyval["ParameterValue"]
            break
    return bucket


def execute_command(cmd: str, show_output: bool = True):
    print(cmd)
    print()
    try:
        result = subprocess.run(cmd.split(" "), shell=False, capture_output=True)
    except FileNotFoundError as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    err = result.stderr.decode("utf-8")
    out = result.stdout.decode("utf-8")
    if result.returncode > 0:
        msg = []
        msg.append("Command failed:")
        msg.append(f"{out}")
        msg.append(f"{err}")
        full_msg = "\n".join(msg)
        print(f"{full_msg}", file=sys.stderr)
        sys.exit(1)
    else:
        if show_output:
            print(f"{out}")


def main():
    parser = argparse.ArgumentParser(description='Execute stack ops, lambda upload')
    help_msg = "[c]reate the stack; [d]estroy the stack; [v]alidate stack files; [u]pload lambda zip file to S3 bucket"
    parser.add_argument('command', choices=['c', 'd', 'v', 'u'], help=help_msg)
    args = parser.parse_args()
    command = vars(args)["command"]

    if command == "c":
        create()
    elif command == "d":
        destroy()
    elif command == "u":
        upload()
    elif command == "v":
        validate()
    else:
        print(f"unknown command: {command}", file=sys.stderr)
        sys.exit(1)

    """
    # Python 3.10 code, for future use...
    match command:
        case "c":
            create()
        case "d":
            destroy()
        case "u":
            upload()
        case "v":
            validate()
        case _:
            print(f"unknown command: {command}", file=sys.stderr)
            sys.exit(1)
    """


if "__main__" == __name__:
    main()

# end of script
