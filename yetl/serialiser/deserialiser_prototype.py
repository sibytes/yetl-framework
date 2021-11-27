# from ..metaconf import Project


def deserialise(name: str, data: dict):

    return deserialise_dict(name, data)


def deserialise_dict(name: str, data: dict):

    print(f"{name} = {name}()")

    for k, v in data.items():

        if isinstance(v, dict):
            deserialise_dict(k, v)
        elif isinstance(v, list):
            deserialise_list(k, v)
        else:
            print(f"\t{k}:{type(v).__name__} = {v}")


def deserialise_list(name: str, data: list):

    list_type = name[:-1]
    print(f"\t{name}:List[{list_type}] = list()")

    for v in data:

        if isinstance(v, dict):
            deserialise_dict(list_type, v)
        elif isinstance(v, list):
            deserialise_list(name, v)
        else:
            print(f"\t\t{name}.append({v})")

