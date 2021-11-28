from ._types import types


def deserialise(name: str, data: dict):

    return _deserialise_dict(name, data)


def _deserialise_dict(name: str, data: dict):
    """Deserialise a dictionary into an object with a defined type or dynamically
    """
    type_ref = types.get(name)

    if not type_ref:
        # if we no type defined then just default to what's in the dictionary
        # and set the base class to an object.
        d_class = _class_factory(name, data, tuple([object]))

    elif isinstance(type_ref["type"], str):
        # if we haven't declared a static class type then create
        # a class dynamically using our definition. We use this
        # approach since we can configure base classes and names
        d_class = _class_factory(type_ref["type"], data, type_ref["base"])

    else:
        # otherwise just use the static type that's in the project.
        d_class = type_ref["type"]

    args = {}
    for k, v in data.items():

        if isinstance(v, dict):
            t = _deserialise_dict(k, v)
            if k in types.keys():
                name = types[k]["name"]
            else:
                name = k
            args[name] = t

        elif isinstance(v, list):
            l = _deserialise_list(k, v)
            if k in types.keys():
                name = types[k]["name"]
            else:
                name = k
            args[name] = l

        else:
            args[k] = v

    d_instance = d_class(**args)

    return d_instance


def _deserialise_list(name: str, data: list):
    """Deserialise a list into a list with a defined type or dynamically
    """
    list_type_ref = types.get(name)

    # create the list and class name of items
    if list_type_ref:
        # we've defined a list type so use that
        list: list_type_ref["type"] = []
        name = list_type_ref["items"]
    else:
        # we have no list type defined so default
        # to a general list and class name for list items
        list = []
        name = f"{name}Item"

    for v in data:
        if isinstance(v, dict):

            t = _deserialise_dict(name, v)
            list.append(t)

        elif isinstance(v, list):

            l = _deserialise_list(name, v)
            list.append(l)

        else:
            list.append(v)

    return list


def _class_factory(class_name: str, arg_names: dict, base_classes=(object)):
    """Dynamically create a class

    Create a class dynamically which can be useful for prototyping and speed of development

    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in arg_names.keys():
                raise TypeError(
                    f"Argument {key} not valid for {self.__class__.__name__}"
                )
            setattr(self, key, value)

    new_class = type(class_name, base_classes, {"__init__": __init__})

    return new_class
