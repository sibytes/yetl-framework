# from pyspark.sql import Row, DataFrame, SparkSession
# from pyspark.sql.functions import *
# from pyspark.sql.types import *
# from yetl.yetl import Yetl
# from yetl import yetl



# df = yetl.spark.sql("select 1")
# df.show()
    

from yetl.metasource.meta_source_file import MetasourceFile

import jinja2

templateLoader = MetasourceFile(searchpath="./project")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "datastore/test.yml"
template = templateEnv.get_template(TEMPLATE_FILE)
# print(templateEnv.list_templates())
outputText = template.render()  # this is where to put args to the template renderer

print(outputText)
