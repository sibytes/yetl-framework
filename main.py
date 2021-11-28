from pyspark.sql import Row, DataFrame, SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from yetl.serialiser.serialiser import serialise, Format
from yetl.yetl import Yetl
from yetl.serialiser.deserialiser import deserialise
from yetl.metaconf import Project


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
    fullnames = [data[0] for data in df.select("fullname").collect()]
    assert fullnames == ["Terry Merry", "Berry Gederry", "Larry Tarry"]

# so the idea is that we're going to use decorators
# to add environment spark configuration to spark 
# code that run anywhere e.g. cloud, local, bare metal
# also we want to manipulate the df that gets passed in
# in local it's handy to DF's from test data defined so I can just TDD a spark function
# when I deploy though it need to chain the DF's together in a pipline.
@Yetl.transform(
    test_df=get_test_customer_df,
    # could use this approach to compose data expectations.
    # here am just doing a simple assert
    test_assert=transform_customer_assert
    )
def transform_customer(df:DataFrame=None):

    # do stranformations
    transformed_df = (df.withColumn("fullname", 
        concat_ws(" ", col("firstname"), col("lastname") ))
    )
    return transformed_df


import yaml
if __name__ == "__main__":
    
    with open("./project/project.yml", "r") as f:
        project_dict = yaml.safe_load(f)

    project:Project = deserialise("project", project_dict)
    data = serialise(project, Format.YAML)

    # print(type(project.environments[1].spark))
    project_dict = yaml.safe_load(data)
    project:Project = deserialise("project", project_dict)
    print(project.environments[0].name)

    # df = transform_customer()
    # df.show()
