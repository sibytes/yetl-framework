import functools
from pyspark.sql import DataFrame

class Yetl():


    def transform(test_df:DataFrame):
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
                    return func(test_df())
                else:
                    return func(*args, **kwargs)

            return wrapper
        return decorator
