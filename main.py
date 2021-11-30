from pyspark.sql import Row, DataFrame, SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from yetl.yetl import Yetl

from yetl import yetl



df = yetl.spark.sql("select 1")
df.show()
    


