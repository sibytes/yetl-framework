# from pyspark.sql import Row, DataFrame, SparkSession
# from pyspark.sql.functions import *
# from pyspark.sql.types import *
# from yetl.yetl import Yetl
# from yetl import yetl



# df = yetl.spark.sql("select 1")
# df.show()



import jinja2
from yetl.metasource.metasource import FileMetasource
from jinja2 import Undefined
import logging



templateLoader = FileMetasource(searchpath="./project")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "Datastore!./datastore/deltalake.yml!datastores!raw_stripe"
template = templateEnv.get_template(TEMPLATE_FILE)
parameters = templateLoader.get_parameters(TEMPLATE_FILE)

print(templateEnv.list_templates())
# print(parameters)


with open("./test_dump.yml", "w") as f:
    f.write(template.render(parameters))