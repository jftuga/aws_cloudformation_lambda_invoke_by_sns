r"""
vpc_info.py
-John Taylor
2021-12-29

From the given region, return VPC subnet information such as vpc id, security groups, subnets
"""
import boto3
import sys


class VpcInfo:
    def __init__(self, region_name: str, vpc_name=""):
        self.region_name = region_name
        self.vpc_name = vpc_name
        self.use_default = True if "" == self.vpc_name else False
        self.subnets = []

        self.session = boto3.Session(region_name=self.region_name)
        self.ec2_resource = self.session.resource("ec2")
        self.ec2_client = self.session.client("ec2")
        self.all_vpcs = self.ec2_client.describe_vpcs()

        self.vpc_id = None
        self.vpc_id = self.get_vpc_id()
        self.vpc = self.ec2_resource.Vpc(self.vpc_id)

    def get_vpc_id(self) -> str:
        if self.vpc_id:
            return self.vpc_id

        # print(f"{self.use_default=}")
        for vpc in self.ec2_resource.vpcs.all():
            # print(f"{vpc.id}")
            if self.use_default and vpc.is_default:
                self.vpc_id = vpc.id
                return self.vpc_id
            if not vpc.tags:
                continue
            for tag in vpc.tags:
                # print(f"    {tag=}")
                if tag['Key'] == 'Name' and tag['Value'] == self.vpc_name:
                    self.vpc_id = vpc.id
                    break
        return self.vpc_id

    def get_subnets(self) -> tuple:
        subnet_ids = []
        for subnet in self.vpc.subnets.all():
            subnet_ids.append(subnet.id)
        return tuple(subnet_ids)

    def get_security_groups(self) -> tuple:
        security_group_ids = []
        for sg in self.vpc.security_groups.all():
            security_group_ids.append(sg.id)
        return tuple(security_group_ids)

    def get_security_group_from_name(self, group_name: str) -> str:
        group_name_lower = group_name.lower()
        for sg in self.vpc.security_groups.all():
            # print(sg.group_name)
            if sg.group_name.lower() == group_name_lower:
                return sg.id
        return None


if "__main__" == __name__:
    if len(sys.argv) != 2:
        print("Give AWS region on command line")
        print("Example: us-east-1")
        sys.exit(1)

    region = sys.argv[1]
    vpc_info = VpcInfo(region)
    vpc_id = vpc_info.get_vpc_id()
    print(f"{vpc_id=}")

    subnets = vpc_info.get_subnets()
    print(f"{subnets=}")

    sec_groups = vpc_info.get_security_groups()
    print(f"{sec_groups=}")

    name = "default"
    print(f"{vpc_info.get_security_group_from_name(name)=}")

    name = "launch-wizard-1"
    print(f"{vpc_info.get_security_group_from_name(name)=}")
