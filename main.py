from pyspark.sql import Row, DataFrame, SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from yetl.yetl import Yetl


def get_test_customer_df(): #(spark:SparkSession):
    # create test dataset
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
    return df


def transform_customer_assert(df:DataFrame):
    # do assertions
    assert True


@Yetl.transform(
    test_df=get_test_customer_df,
    test_assert=transform_customer_assert
    )
def transform_customer(df:DataFrame=None):

    # do stranformations
    transformed_df = (df.withColumn("Full Name", 
        concat_ws(" ", col("firstname"), col("lastname") ))
    )
    return transformed_df



if __name__ == "__main__":

    df = transform_customer()
    df.show()
