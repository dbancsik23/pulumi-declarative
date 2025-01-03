from dataclasses import field
from typing import List, Optional, Dict

import pulumi
import pulumi_aws
from attr import dataclass

from libs.security_group.RuleType import RuleType


class AwsSecurityGroup:
    def __init__(
            self,
            name: str,
            vpc_id: str,
            ingress: List[Dict],
            egress: Optional[List[Dict]] = None,
    ):
        self.env = pulumi.get_stack()
        self.name = f"{name}-{self.env}-sg"
        self.vpc_id = vpc_id
        self.ingress = ingress
        self.egress = egress or self.default_egress()
        self.description = f"Security Group for {self.name}"

    @staticmethod
    def default_egress():
        return [{
            "rule_type": RuleType.EGRESS.name.lower(),
            "from_port": 0,
            "to_port": 0,
            "protocol": "-1",
            "cidr_blocks": ["0.0.0.0/0"]
        }]

    def create_security_group(self):
        ingress_rules = [self.create_sg_rule(**rule) for rule in self.ingress]
        egress_rules = [self.create_sg_rule(**rule) for rule in self.egress]

        sg = pulumi_aws.ec2.SecurityGroup(
            self.name,
            description=self.description,
            vpc_id=self.vpc_id,
            egress=egress_rules,
            ingress=ingress_rules,
            tags={"Name": self.name, "Environment": self.env},
        )

        pulumi.export(f"{self.name}_sg_id", sg.id)
        return sg.id.apply(lambda s_id: {"sg_id": s_id})

    @staticmethod
    def create_sg_rule(
            rule_type: str,
            from_port: int,
            to_port: int,
            protocol: str,
            cidr_blocks: Optional[List[str]] = None,
            prefix_list_ids: Optional[List[str]] = None,
            security_groups: Optional[List[str]] = None,
    ) -> Dict:
        def default_list(value: Optional[List[str]]) -> List[str]:
            return value if value else []

        return {
            "from_port": from_port,
            "to_port": to_port,
            "protocol": protocol,
            "cidr_blocks": default_list(cidr_blocks),
            "description": f"{RuleType[rule_type.upper()]} Security Group rule allowing {protocol} traffic on ports {from_port}-{to_port}",
            "prefix_list_ids": default_list(prefix_list_ids),
            "security_groups": default_list(security_groups),
            "self": False,
        }
