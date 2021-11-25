import functools
from pyspark.sql import DataFrame, SparkSession
from types import FunctionType

class Yetl():


    def transform(
        test_df:FunctionType,
        test_assert:FunctionType = None
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
                    ret = func(test_df())
                else:
                    ret = func(*args, **kwargs)

                if test_assert:
                    test_assert(ret)
                
                return ret

            return wrapper
        return decorator

