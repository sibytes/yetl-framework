from ..metaconf import *
from typing import List

types = {
    "project": {"name": "project", "type": "Project", "base": None},
    "environments": {"name": "environments", "type": "List[Environment]", "base": None},
    "environment": {"name": "environment", "type": "Environment", "base": None},
    "secrets_file": {
        "name": "secret_store",
        "type": "SecretsFile",
        "base": SecretStore,
    },
    "databricks_scope": {
        "name": "secret_store",
        "type": "DatabricksScope",
        "base": SecretStore,
    },
    "spark": {"name": "spark", "type": "StandardSpark", "base": Spark},
    "azure_databricks": {"name": "spark", "type": "AzureDatabricks", "base": Spark},
}
