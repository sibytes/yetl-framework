import functools
from pyspark.sql import DataFrame, SparkSession
from types import FunctionType
from .metaconf import Project
from .serialiser import deserialise
import yaml

class Yetl():

    def builder(path:str="./project"):
        project_path = f"{path}/project.yml"

        with open(project_path, "r") as f:
            project_dict = yaml.safe_load(f)

        project:Project = deserialise("project", project_dict)

        return project

    def spark(
        path:str
    ):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):

                project = Yetl.builder(path)
                spark = project.environments[0].spark

                # create test dataset
                spark = (SparkSession
                        .builder
                        .master(spark.master)
                        .appName(spark.app_name)
                        .getOrCreate())

                ret = func(spark)
                
                return ret

            return wrapper
        return decorator




    def transform(
        df_function:FunctionType,
        assert_function:FunctionType = None
    ):
        def decorator(func):
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
                    ret = func(df_function(None))
                else:
                    ret = func(*args, **kwargs)

                if assert_function:
                    assert_function(ret)
                
                return ret

            return wrapper
        return decorator

