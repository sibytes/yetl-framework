
from collections import ChainMap


def get_api_version(api_version_uri:str):

    # TODO: Need a better validator, probably a regex
    if api_version_uri.startswith("yetl-framework.io/"):
        p = api_version_uri.split("/")
        if int(p[1]) != 1 or len(p) != 4:
            raise Exception("invalid api_version uri version")

        api_version = {
            "namespace": p[0],
            "version": p[1],
            "base": p[2],
            "type": p[3]
        }
        return api_version
    else:
        raise Exception("invalid api_version uri")


def stitch_defaults(data: dict):

    for k, v in data.items():

        if k == "apiVersion":
            api_version = get_api_version(v)

        if isinstance(v, list):

            default = next(i for i in v if i["id"] == "default")
            default["apiVersion"] = api_version
            defaulted = list()
            for i in v:

                if i["id"] != "default":
                    # merge in defaults
                    n = dict(ChainMap(i, default))
                    defaulted.append(n)

            data[k] = defaulted



        







