# from pyspark.sql import Row, DataFrame, SparkSession
# from pyspark.sql.functions import *
# from pyspark.sql.types import *
# from yetl.yetl import Yetl
# from yetl import yetl



# df = yetl.spark.sql("select 1")
# df.show()



    

# from yetl.metasource import meta_composer
# import yaml
# with open("./project/datastore/deltalake.yml", "r") as f:
#     data:dict = yaml.safe_load(f)
# meta_composer.stitch_defaults(data)
# class NoAliasDumper(yaml.Dumper):
#     def ignore_aliases(self, data):
#         return True
# print(yaml.dump(data, indent=4, Dumper=NoAliasDumper))


# import jinja2
# from yetl.metasource.meta_source_file import MetasourceFile
# templateLoader = MetasourceFile(searchpath="./project")
# print(templateLoader.list_templates())



# templateLoader = MetasourceFile(searchpath="./project")
# templateEnv = jinja2.Environment(loader=templateLoader)
# TEMPLATE_FILE = "datastore/test.yml"
# template = templateEnv.get_template(TEMPLATE_FILE)
# # print(templateEnv.list_templates())
# outputText = template.render()  # this is where to put args to the template renderer

# print(outputText)



import yaml

from yetl.metasource.metasource import FileMetasource
fm = FileMetasource("./project")

class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True
        
print(yaml.dump(fm.master_metadata, indent=4, Dumper=NoAliasDumper))