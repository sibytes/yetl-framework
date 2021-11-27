from ..metaconf import *
from typing import List

types = {
    "project": {"type": "Project", "base": None},
    "environments": {"type": "List[Environment]", "base": None},
    "environment": {"type": "Environment", "base": None},
    "secrets_file": {"type": "SecretsFile", "base": SecretStore},
    "databricks_scope": {"type": "DatabricksScope", "base": SecretStore},
    "spark": {"type": "StandardSpark", "base": Spark},
    "azure_databricks": {"type": "AzureDatabricks", "base": Spark},
}

# apiVersion: yetl-framework.io/en/1/project

# environments:

#   - name: local
#     project: ./project
#     secretstore:
#       provider: local
#       # important: in real projects ensure this file is in .gitignore
#       store: ./project/secrets.yml
#     spark:
#       master: local[2]
#       config: null

#   - name: development
#     project: dbfss://yetl/jaffle_shop/project
#     secretstore:
#       provider: databricks
#       # databricks scope that holds the secrets
#       # can be keyvault backed
#       store: kv_dataplatform
#     azure_databricks:
#       workspace_url: ttps://adb-8723178682600000.0.azuredatabricks.net/
#       org_id: 8723178682600000
#       # secret that holds the token
#       token: databricks_pat
#       port: 5554
#       cluster: 0921-001415-jelly628
