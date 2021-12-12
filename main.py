# from pyspark.sql import Row, DataFrame, SparkSession
# from pyspark.sql.functions import *
# from pyspark.sql.types import *
# from yetl.yetl import Yetl
# from yetl import yetl



# df = yetl.spark.sql("select 1")
# df.show()



from jinja2 import DebugUndefined
from pprint import pprint
from yetl.metasource.metasource import FileMetasource
import jinja2

templateLoader = FileMetasource(searchpath="./project")
templateEnv = jinja2.Environment(loader=templateLoader, undefined=DebugUndefined)
pprint(templateEnv.list_templates(filter_func=FileMetasource.template_filter("Datastore")))
TEMPLATE_FILE = 'Datastore!Adls!./project/datastore/landing.yml!datastores!landing_jaffleshop'
template = templateEnv.get_template(TEMPLATE_FILE)

with open("./test_dump.yml", "w") as f:
    f.write(template.render(templateLoader.get_parameters(TEMPLATE_FILE)))




