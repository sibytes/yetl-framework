import functools
from pyspark.sql import Row, DataFrame, SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructField, StructType, StringType, LongType

class Yetl():

    def repeat(num_times):
        def decorator_repeat(func):
            @functools.wraps(func)
            def wrapper_repeat(*args, **kwargs):
                for _ in range(num_times):
                    value = func(*args, **kwargs)
                return value
            return wrapper_repeat
        return decorator_repeat


    def transform(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            if (
                    not (
                        args
                        or "df" in kwargs 
                        or kwargs.get("df", None)
                    )
                    or (args and not args[0])
                ):

                # need to pass this from a test decorator
                spark = (SparkSession
                        .builder
                        .master("local")
                        .appName("Spark SQL basic example")
                        .getOrCreate())

                schema = StructType([
                    StructField("id", StringType(), True),
                    StructField("firstname", StringType(), True),
                    StructField("lastname", StringType(), True)
                ])

                rows = [Row(1, "Terry", "Merry"), 
                        Row(2, "Berry", "Gederry"), 
                        Row(3, "Larry", "Tarry")]

                df = spark.createDataFrame(rows, schema)
            
                return func(df)
            else:
                return func(*args, **kwargs)

        return wrapper
