# from pyspark.sql import Row, DataFrame, SparkSession
# from pyspark.sql.functions import *
# from pyspark.sql.types import *
# from yetl.yetl import Yetl
# from yetl import yetl



# df = yetl.spark.sql("select 1")
# df.show()


from re import template
from jinja2 import DebugUndefined, Undefined
from pprint import pprint
from yetl.metasource import Builder
import yaml
import os, shutil

class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True

templates = Builder.build("./project", Undefined)

test_dir = "./test_build"
if os.path.exists(test_dir) and os.path.isdir(test_dir):
    shutil.rmtree(test_dir)

for i in templates:
    base = i["datastore"]["apiVersion"]["base"]
    type = i["datastore"]["apiVersion"]["type"]
    datastore_name = i["datastore"]["name"]
    schema_name = i["datastore"]["schema"]
    try:
        dataset_name = i["dataset"]["default"]["name"]
    except:
        pass
    try:
        dataset_name = i["dataset"]["permissive"]["name"]
    except:
        pass
    try:
        dataset_name = i["dataset"]["name"]
    except:
        pass

    path = f"./{test_dir}/{base}/{type}"
    if not os.path.exists(path):
        os.makedirs(path)

    path = f"{path}/{datastore_name}_{schema_name}_{dataset_name}.yml"

    with open(path, "w") as f:
        f.write(yaml.dump(i, indent=4, Dumper=NoAliasDumper))


