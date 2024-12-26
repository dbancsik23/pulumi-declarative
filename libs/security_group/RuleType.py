from enum import Enum


class RuleType(Enum):
    INGRESS = "ingress"
    EGRESS = "egress"