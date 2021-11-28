from ..metaconf import *
from typing import List
"""Holds a type dictionary that is used to map complex deserialisations

Our deserialisation needs are complex and this dictionary just helps
to simplify the deserialisation logic. By using this method we can
configure:
    - What base objects deserialised objects have
    - Whether to use a static class or a dynamic one to save on effort
    - standardising tag names with variable names
    - Specifically typing lists
"""

types = {
    "project": {"name": "project", "type": Project, "base": None},
    "environments": {"name": "environments", "type": List[Environment], "items": "environment"},
    "environment": {"name": "environment", "type": Environment, "base": None},
    "secrets_file": {
        "name": "secrets_file",
        "type": "SecretsFile",
        "base": tuple([SecretStore]),
    },
    "databricks_scope": {
        "name": "databricks_scope",
        "type": "DatabricksScope",
        "base": tuple([SecretStore]),
    },
    "spark": {"name": "spark", "type": "StandardSpark", "base": tuple([Spark])},
}
