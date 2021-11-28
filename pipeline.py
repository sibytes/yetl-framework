from pyspark.sql import Row, DataFrame, SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from yetl.yetl import Yetl


@yetl(
    dataset="customer",
    source_datastore="landing_jaffleshop_jaffleshop",
    destination_datastore="raw_jaffleshop_jaffleshop" 
)
def load_customer_into_raw(source_df:DataFrame):

    # do tranformations
    desination_df = source_df
    return desination_df

@yetl(
    dataset="customer",
    source_datastore="landing_jaffleshop_jaffleshop",
    destination_datastore="raw_jaffleshop_jaffleshop"
)
def load_customer_into_prepared_1(source_df:DataFrame):

    # do tranformations
    desination_df_1 = (source_df.withColumn("fullname", 
        concat_ws(" ", col("firstname"), col("lastname") ))
    )
    desination_df_2 = load_customer_into_prepared_2(desination_df_1)

    return desination_df_2


def load_customer_into_prepared_2(source_df:DataFrame):

    # do tranformations
    desination_df = (source_df.withColumn("fullname", 
        concat_ws(" ", col("firstname"), col("lastname") ))
    )
    return desination_df


if __name__ == "__main__":
    
    project = yetl.build()

    project.process(destination_datastore="raw_jaffleshop_jaffleshop", dataset="customer")

