from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import yetl


@yetl.process(
    dataset="customer",
    source_datastore="landing_jaffleshop_jaffleshop.jaffleshop",
    destination_datastore="raw_jaffleshop_jaffleshop.jaffleshop",
)
def load_customer_into_raw(spark: SparkSession, source_df: DataFrame):

    # do tranformations
    desination_df = source_df
    return desination_df


@yetl.process(
    dataset="customer",
    source_datastore="raw_jaffleshop_jaffleshop.jaffleshop",
    destination_datastore="jaffleshop",
)
def load_customer_into_prepared_1(spark: SparkSession, source_df: DataFrame):

    # do tranformations
    desination_df_1 = source_df
    desination_df_2 = load_customer_into_prepared_2(desination_df_1)

    return desination_df_2


def load_customer_into_prepared_2(spark: SparkSession, source_df: DataFrame):

    # do tranformations
    desination_df = source_df.withColumn(
        "fullname", concat_ws(" ", col("firstname"), col("lastname"))
    )
    return desination_df


if __name__ == "__main__":

    project = yetl.builder()
    # if transform methods are called without a yetl process
    # the decorator passthroughs should bypass
    # this allows the framework spark to be testable.
    project.process(
        destination_datastore="raw_jaffleshop_jaffleshop", dataset="customer"
    )
