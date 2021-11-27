# from ..metaconf import Project
from .types import types

def deserialise(name: str, data: dict):

    return _deserialise_dict(name, data)


def _deserialise_dict(name: str, data: dict):

    type_ref = types.get(name)
    if isinstance(type_ref["type"], str):
        d_class = _class_factory(type_ref["type"], data, type_ref["base"])
    else:
        d_class = type_ref["type"]
    
    args = {}
    for k, v in data.items():

        if isinstance(v, dict):
            _deserialise_dict(k, v)
        elif isinstance(v, list):
            _deserialise_list(k, v)
        else:
            args[k] = v

    d_instance = d_class(**data)

    return d_instance

# TODO
def _deserialise_list(name: str, data: list):
    pass 
    # list_type = name[:-1]
    # print(f"\t{name}:List[{list_type}] = list()")

    # for v in data:

    #     if isinstance(v, dict):
    #         deserialise_dict(list_type, v)
    #     elif isinstance(v, list):
    #         deserialise_list(name, v)
    #     else:
    #         print(f"\t\t{name}.append({v})")


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
