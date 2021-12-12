# from pyspark.sql import Row, DataFrame, SparkSession
# from pyspark.sql.functions import *
# from pyspark.sql.types import *
# from yetl.yetl import Yetl
# from yetl import yetl



# df = yetl.spark.sql("select 1")
# df.show()


from pprint import pprint
from yetl.metasource.metasource import Builder
templates = Builder.build("./project")

for i in range(len(templates)):
    with open(f"./test_build/test_build_{i}.yml", "w") as f:
        f.write(templates[i])


