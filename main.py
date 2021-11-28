from pyspark.sql import Row, DataFrame, SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from yetl.yetl import Yetl


@Yetl.spark(
    path = "./project"
)
def get_customer(spark:SparkSession = None):

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
    fullnames = [data[0] for data in df.select("fullname").collect()]
    assert fullnames == ["Terry Merry", "Berry Gederry", "Larry Tarry"]


@Yetl.transform(
    source_df=get_customer,
    assert_function=transform_customer_assert
    )
def transform_customer(df:DataFrame = None):

    # do tranformations
    transformed_df = (df.withColumn("fullname", 
        concat_ws(" ", col("firstname"), col("lastname") ))
    )
    return transformed_df



if __name__ == "__main__":
    
    df = transform_customer()
    df.show()
