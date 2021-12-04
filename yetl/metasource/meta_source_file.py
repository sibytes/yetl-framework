from jinja2 import BaseLoader, TemplateNotFound
from os.path import join, exists, getmtime
from typing import List

class MetasourceFile(BaseLoader):

    def __init__(self, path:str) -> None:

        self.path = path


    def get_source(self, environment, template):

        path = join(self.path, template)

        if not exists(path):
            raise TemplateNotFound

        mtime = getmtime(path)
        with open(path) as f:
            source = f.read()

        return source, path, lambda: mtime == getmtime(path)

    def list_templates(self) -> List[str]:
        return []

