import base64
from dataclasses import dataclass
from typing import Optional, List, Dict

import pulumi
import pulumi_aws as aws
from pulumi_aws.ec2 import InstanceLaunchTemplateArgs

from libs.helper import PulumiHelper as helper


@dataclass(init=False)
class AwsEC2Instance:
    name: str
    instance_type: str
    ami_id: str
    vpc_security_group_ids: List[str]
    subnet_id: Optional[str]
    key_name: Optional[str]
    tags: Dict[str, str]
    additional_volumes: Optional[List[Dict[str, str]]] = None
    user_data: Optional[str] = None
    _user_data_base64: Optional[str] = None

    def __init__(
            self,
            name: str,
            instance_type: str,
            ami_id: str,
            vpc_security_group_ids: Optional[List[str]] = None,
            subnet_id: Optional[str] = None,
            key_name: Optional[str] = None,
            tags: Optional[Dict[str, str]] = None,
            additional_volumes: Optional[List[Dict[str, str]]] = None,
            user_data: Optional[str] = None,
            launch_template=None,
            user_data_base64: Optional[str] = None,
            private_ip: Optional[str] = None,
            availability_zone: pulumi.Input[str] = None,
            iam_instance_profile: Optional[str] = None,
            associate_public_ip_address: Optional[bool] = True
    ):
        self.env = pulumi.get_stack()
        self.name: str = f"{name}-{self.env}"
        self.instance_type: str = instance_type
        self.ami_id: str = ami_id
        self.vpc_security_group_ids: List[str] = vpc_security_group_ids or []
        self.subnet_id: Optional[str] = subnet_id
        self.key_name: Optional[str] = key_name
        self.default_tags = helper.default_tags(self.name)
        self.tags: Dict[str, str] = tags or self.default_tags
        self.additional_volumes: Optional[List[Dict[str, str]]] = additional_volumes or []
        self.launch_template: InstanceLaunchTemplateArgs = launch_template
        self.user_data: str = user_data
        self._user_data_base64: str = user_data_base64
        self.private_ip: str = private_ip
        self.availability_zone: str = availability_zone
        self.iam_instance_profile: str = iam_instance_profile
        self.associate_public_ip_address: bool = associate_public_ip_address

    @property
    def user_data_base64(self):
        return self._user_data_base64

    @user_data_base64.setter
    def user_data_base64(self, user_data):
        self._user_data_base64 = self.encode(user_data)

    def create_instance(self):
        instance = aws.ec2.Instance(
            self.name,
            instance_type=self.instance_type,
            ami=self.ami_id,
            vpc_security_group_ids=self.vpc_security_group_ids,
            subnet_id=self.subnet_id,
            key_name=self.key_name,
            tags=self.tags,
            associate_public_ip_address=self.associate_public_ip_address,
            launch_template=self.launch_template,
            user_data=self.user_data,
            user_data_base64=self._user_data_base64,
            private_ip=self.private_ip,
            availability_zone=self.availability_zone,
            iam_instance_profile=self.iam_instance_profile

        )

        for idx, volume in enumerate(self.additional_volumes, start=1):
            aws.ec2.VolumeAttachment(
                f"{self.name}-vol-{idx}",
                instance_id=instance.id,
                volume_id=volume["volume_id"],
                device_name=volume["device_name"],
            )

        pulumi.export(f"{self.name}_instance_id", instance.id)
        pulumi.export(
            f"{self.name}_details",
            instance.id.apply(lambda id: f"Instance {self.name} created with ID: {id}")
        )

        pulumi.export(f"{self.name}_instance_id", instance.id)
        pulumi.export(f"{self.name}_public_ip", instance.public_ip)

    @staticmethod
    def encode(user_data):
        if user_data:
            return base64.b64encode(user_data.encode("utf-8")).decode("utf-8")
