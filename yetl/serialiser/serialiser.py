import json
import yaml
from enum import Enum


class Format(Enum):
    JSON = 1
    YAML = 2
    DICT = 3


def serialise(obj: object, format_type: Format = Format.YAML):

    data = json.dumps(obj, default=lambda o: o.__dict__, indent=4)

    if format_type in (Format.YAML, Format.DICT):
        data = json.loads(data)

    if format_type == Format.YAML:
        data = yaml.dump(data, indent=4)

    return data
