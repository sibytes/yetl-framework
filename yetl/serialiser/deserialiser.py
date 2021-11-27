from .types import types


def deserialise(name: str, data: dict):

    return _deserialise_dict(name, data)


def _deserialise_dict(name: str, data: dict):

    type_ref = types[name]
    if isinstance(type_ref["type"], str):
        d_class = _class_factory(type_ref["type"], data, type_ref["base"])
    else:
        d_class = type_ref["type"]

    args = {}
    for k, v in data.items():

        if isinstance(v, dict):
            t = _deserialise_dict(k, v)
            name = types[k]["name"]
            args[name] = t

        elif isinstance(v, list):
            l = _deserialise_list(k, v)
            name = types[k]["name"]
            args[name] = l
        else:
            args[k] = v

    d_instance = d_class(**args)

    return d_instance


def _deserialise_list(name: str, data: list):

    list_type_ref = types[name]

    # create the list
    list:list_type_ref["type"] = []

    for v in data:
        if isinstance(v, dict):
            t = _deserialise_dict(list_type_ref["items"], v)
            list.append(t)

        elif isinstance(v, list):
            l = _deserialise_list(list_type_ref["items"], v)
            list.append(l)

        else:
            list.append(v)

    return list


def _class_factory(class_name: str, arg_names: dict, base_classes=(object)):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in arg_names.keys():
                raise TypeError(
                    f"Argument {key} not valid for {self.__class__.__name__}"
                )
            setattr(self, key, value)

    new_class = type(class_name, base_classes, {"__init__": __init__})

    return new_class
