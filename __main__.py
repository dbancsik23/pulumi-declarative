"""An AWS Python Pulumi program"""
import json

import pulumi

from libs.ec2 import AwsEC2Instance
from libs.helper import PulumiHelper as helper
from libs.iam import AwsIAMRole, AssumeRoleService
from libs.security_group import AwsSecurityGroup

config = pulumi.Config().require("cloud")
config = json.loads(config)
security_group = AwsSecurityGroup(**config['security_group']).create_security_group()

iam_role = AwsIAMRole(**config['iam_role'])
assume_role_policy = iam_role.generate_assume_role_policy(AssumeRoleService.EC2)
iam_role.assume_role_policy = assume_role_policy
role = iam_role.create_role()

ec2_instance = AwsEC2Instance(**config['ec_instance'])
ec2_instance.vpc_security_group_ids = [security_group["sg_id"]]
ec2_instance.user_data_base64 = helper.read_user_data()
ec2_instance.iam_instance_profile = role["instance_profile_name"]["name"]
ec2_instance.create_instance()
