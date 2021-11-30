import functools
from pyspark.sql import DataFrame, SparkSession
from types import FunctionType
from .metaconf import Project, Spark
from .serialiser import deserialise
import yaml
import inspect
from abc import ABC
import os

def _create_spark(project:Project, environment:str):

    try:
        env = next(e for e in project.environments if e.name == environment)
    except StopIteration:
        msg = f"Project environment {environment} cannot be found."
        raise Exception(msg)

    spark = env.spark.create_spark()

    return spark


def _deserialise_project(project_path:str):

    with open(project_path, "r") as f:
        project_dict = yaml.safe_load(f)

    project:Project = deserialise("project", project_dict)

    return project

home = os.getenv("YELT_HOME")
environment = os.getenv("YELT_ENV")

if not home:
    home = "./project"

if not environment:
    environment = "local"

project_path = f"{home}/project.yml"
project = _deserialise_project(project_path)
spark = _create_spark(project, environment)


class Yetl:

    def __init__(self) -> None:

        self.home = os.getenv("YELT_HOME")
        self.environment = os.getenv("YELT_ENV")

        if not self.home:
            self.home = "./project"

        if not self.environment:
            self.environment = "local"

        self.project_path = f"{self.home}/project.yml"
        self.project = self._deserialise_project(self.project_path)
        self.spark = self._create_spark(self.project, self.environment)




# def spark(
#     path:str
# ):
#     def decorator(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):

#             if "spark" in inspect.getfullargspec(func).args:

#                 project = Yetl.builder(path)
#                 spark = project.environments[0].spark

#                 # create test dataset
#                 spark = (SparkSession
#                         .builder
#                         .master(spark.master)
#                         .appName(spark.app_name)
#                         .getOrCreate())

#                 kwargs["spark"] = spark

#             ret = func(*args, **kwargs)
            
#             return ret

#         return wrapper
#     return decorator


# def transform(
#     source_df:FunctionType,
#     assert_function:FunctionType = None
# ):
#     def decorator(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             if (
#                     not (
#                         args
#                         or "df" in kwargs 
#                         or kwargs.get("df", None)
#                     )
#                     or (args and not args[0])
#                 ):
#                 ret = func(source_df())
#             else:
#                 ret = func(*args, **kwargs)

#             if assert_function:
#                 assert_function(ret)
            
#             return ret

#         return wrapper
#     return decorator

