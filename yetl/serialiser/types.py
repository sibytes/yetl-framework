from ..metaconf import *
from typing import List


types = {
    "project": {"name": "project", "type": Project, "base": None},
    # "project": {"name": "project", "type": "Project", "base": tuple([object])},
    "environments": {"name": "environments", "type": List[Environment], "items": "environment"},
    "environment": {"name": "environment", "type": Environment, "base": None},
    "secrets_file": {
        "name": "secret_store",
        "type": "SecretsFile",
        "base": tuple([SecretStore]),
    },
    "databricks_scope": {
        "name": "secret_store",
        "type": "DatabricksScope",
        "base": tuple([SecretStore]),
    },
    "standard_spark": {"name": "spark", "type": "StandardSpark", "base": tuple([Spark])},
    "azure_databricks": {"name": "spark", "type": "AzureDatabricks", "base": tuple([Spark])},
}
