# YETL Framework

Yet another ETL Framework for Spark


How does it work?

Declaritive spark dataframe pipelining frameworking.

1. Define your datastores e.g. `./project/datastores`
2. Define your datasets e.g. `./project/datasets`
3. Write spark extract, transform and load in sql, python or scala just referencing a dataset using yetl api. Api can also be used by orchestration tools to land data from source for spark
4. Create datastore, datasets and workflow documentation automatically
5. Execute workflows compiled from code dataset references in a basic execution engine or other tools e.g. databricks mulistep jobs etc

Progress log:

* 2021-11-21: Done : Metadata design 1st draft prototype
* WIP: Jinja2 Templating and Deserialization: WIP

## Philosophical Goals

- Have fun learning and building something that has no affiliation to anything commercial
- Easy and fun to engineer pipelines
- Can be used in spark everywhere (Spark PaaS, IaaS, baremetal, locally)
- Bar landing the data into HDFS (prem or cloud) spark is all we need
- Excellent metadata configuration and tools - fun, simple, full featured and minimal
- No data loading anti-patterns resulting from poorly designed re-use and metadata
- Can be called if desired seamlessly from any workflow tool integrating transparent lineage
- Support batch and streaming
- Support datalake house add-on's - hudi, deltalake
- Extremely flexible
- Support behavior driven development
- Support test driven developement - Locally, CI/CD agent and remote envs
- Integrate and support data expectation frameworks
- Workflow engine
- Auto document pipelines

## Example Usage

Once metadata is declared we can just create something like the following for a given dataset, many datasets or all datasets

```python
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


@Yetl.transform(
    test_df=get_test_customer_df,
    assert_df=transform_customer_assert
    )
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
```