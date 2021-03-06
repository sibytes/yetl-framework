<img src="https://img.shields.io/badge/Python-v3.8-blue">

# YETL Framework - It's for Spark!

**Y**et another **ETL** **F**ramework for Spark

https://yetl-framework.readthedocs.io/en/latest/

How does it work?

Declaritive spark dataframe pipelining frameworking.

1. Define your datastores e.g. `./project/datastores`
2. Define your datasets e.g. `./project/datasets`
3. Write spark extract, transform and load in sql, python or scala just referencing a dataset using yetl api. Api can also be used by orchestration tools to land data from source for spark
4. Create datastore, datasets and workflow documentation automatically
5. Execute workflows compiled from code dataset references in a basic execution engine or other tools e.g. databricks mulistep jobs etc

Progress log:

* 2021-11-21: Done : Metadata design 1st draft prototype
* 2021-11-28: Done : Dynamic config API deserialiser
* 2021-11-28: Done : Pipeline DSL Draft
* TODO: Jinja2 Templating and Deserialization
* WIP: Proto-typing decorator model

## Philosophical Goals

- Have fun learning and building something that has no affiliation to anything commercial
- Easy and fun to engineer pipelines
- Can be used in spark everywhere (Spark PaaS, IaaS, baremetal, locally)
- Bar landing the data into HDFS (prem or cloud) spark is all we need
- Excellent metadata configuration and tools - fun, simple, full featured and minimal to use
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
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import yetl


@yetl.process(
    dataset="customer",
    source="landing_jaffleshop",
    destination="raw_jaffleshop",
)
def load_customer_into_raw(spark: SparkSession, source_df: DataFrame):

    # do tranformations
    desination_df = source_df
    return desination_df


@yetl.process(
    dataset="customer",
    source="raw_jaffleshop",
    destination="jaffleshop",
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

    project = yetl.builder.create_project()
    # if transform methods are called without a yetl process
    # the decorator passthroughs should bypass
    # this allows the framework spark to be testable.
    # Process by destination object. It just figures out what it needs to process
    project.process(
        datastore="jaffleshop", datasets="customer", process_dependencies=True
    )
```


# Development Setup

Create virual environment and install dependencies for local development:

```
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install --editable .
```


# Build

Build python wheel:
```
python setup.py sdist bdist_wheel
```

There is a CI build configured for this repo that builds on main origin and publishes to PyPi.

# Test

Dependencies for testing:
```
pip install --editable .
```

Run tests:
```
pytest
```

Test Coverage:
```
pytest --cov=autobricks --cov-report=html
```

View the report in a browser:
```
./htmlcov/index.html
```


