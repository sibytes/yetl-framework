from pyspark.sql import Row, DataFrame, SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructField, StructType, StringType, LongType
from yetl.yetl import Yetl


def get_test_customer_df(spark:SparkSession):
    # create test dataset

    test_schema = StructType([
        StructField("id", StringType(), True),
        StructField("firstname", StringType(), True),
        StructField("lastname", StringType(), True)
    ])

    test_rows = [Row(1, "Terry", "Merry"), 
            Row(2, "Berry", "Gederry"), 
            Row(3, "Larry", "Tarry")]

    test_df = spark.createDataFrame(test_rows, test_schema)
    return test_df


@Yetl.transform
def transform_customer(df:DataFrame=None):

    # do stranformations
    transformed_df = (df.withColumn("Full Name", 
        concat_ws(" ", col("firstname"), col("lastname") ))
    )
    return transformed_df



def transform_customer_assert(df:DataFrame):
    # do assertions
    pass


if __name__ == "__main__":

    df = transform_customer()
    df.show()
