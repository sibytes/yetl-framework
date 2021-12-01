
from collections import ChainMap


def get_type(api_version_uri:str):

    if api_version_uri.startswith("yetl-framework.io/en/"):
        p = api_version_uri.split("/")

        if int(p[-3]) != 1:
            raise Exception("invalid api_version uri version")

        return p[-2], p[-1]
    else:
        raise Exception("invalid api_version uri")


def stitch_defaults(data: dict):

    for k, v in data.items():

        if isinstance(v, list):

            default = next(i for i in v if i["id"] == "default")
            defaulted = list()
            for i in v:

                if i["id"] != "default":

                    # merge in defaults
                    n = dict(ChainMap(i, default))
                    defaulted.append(n)

            data[k] = defaulted



        







