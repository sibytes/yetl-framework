from abc import ABC, abstractmethod
from pyspark.sql import SparkSession


class _Spark(ABC):
    @abstractmethod
    def __init__(self, master: str, app_name: str, config: dict):
        pass

    @abstractmethod
    def create_spark() -> SparkSession:
        pass


class Spark(_Spark):
    def __init__(self, master: str, app_name: str, config: dict):
        self.master = master
        self.app_name = app_name
        self.config = config


    def create_spark(self) -> SparkSession:
        if self.config:
            return (
                SparkSession.builder.master(self.master)
                .appName(self.app_name)
                .config(**self.config)
                .getOrCreate()
            )
        else:
            return (
                SparkSession.builder.master(self.master)
                .appName(self.app_name)
                .getOrCreate()
            )

