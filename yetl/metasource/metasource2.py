
from jinja2 import BaseLoader, TemplateNotFound, Environment
from os.path import join, exists, getmtime
import os
import typing as t
from collections import abc
from jinja2.environment import TemplateModule
import yaml

from collections import ChainMap
    

class FileMetasource(BaseLoader):

    _API_VESRION = "apiVersion"
    _API_NAMESPACE = "yetl-framework.io"
    _API_DEFAULT = "default"
    _KEY_SEPERATOR = "!"

    def __init__(
        self,
        searchpath: t.Union[str, os.PathLike, t.Sequence[t.Union[str, os.PathLike]]],
        encoding: str = "utf-8",
        followlinks: bool = False,
    ) -> None:
        """

            Here we need to stitch the usability templates together into the jinja templates
            that we want to render.
        
        """
        if not isinstance(searchpath, abc.Iterable) or isinstance(searchpath, str):
            searchpath = [searchpath]

        self.searchpath = [os.fspath(p) for p in searchpath]
        self.encoding = encoding
        self.followlinks = followlinks

    def _get_api_version(self, api_version_uri:str):

        # TODO: Need a better validator, probably a regex
        if api_version_uri.startswith(f"{self._API_NAMESPACE}/"):
            p = api_version_uri.split("/")
            if int(p[1]) != 1 or len(p) != 4:
                raise Exception(f"invalid {self._API_VESRION} uri version")

            api_version = {
                "namespace": p[0],
                "version": p[1],
                "base": p[2],
                "type": p[3]
            }
            return api_version
        else:
            raise Exception(f"invalid {self._API_VESRION} uri")

    def _lookup_index(data:dict, index:str):

        keys = index.split("!")
        n = data
        for k in keys:
            n = n[k]

        return n

    def _open_if_exists(self, filename: str, mode: str = "rb") -> t.Optional[t.IO]:
        """Returns a file descriptor for the filename if that file exists,
        otherwise ``None``.
        """
        if not os.path.isfile(filename):
            return None

        return open(filename, mode)

    def _index(self):
        """
            
        """
        metadata_index = list()

        for searchpath in self.searchpath:
            walk_dir = os.walk(searchpath, followlinks=self.followlinks)
            for dirpath, _, filenames in walk_dir:
                for filename in filenames:
                    metafile = os.path.join(dirpath, filename)

                    f = self._open_if_exists(metafile)
                    if f is None:
                        continue
                    try:
                        metadata:dict = yaml.safe_load(f)
                    finally:
                        f.close()
                    
                    try:
                        api_version = metadata[self._API_VESRION]
                    except KeyError as e:
                        raise Exception(f"Invalid format {self._API_VESRION} not found", e)

                    api_version = self._get_api_version(api_version)
                    base = api_version["base"]
                    type = api_version["type"]
                    path = f"{searchpath}/{filename}"

                    if base == "Datastore":
                        for k, v in metadata.items():
                            if isinstance(v, dict):
                                for ki, vi in v.items():
                                    if ki != self._API_DEFAULT and isinstance(vi, dict):
                                        keys = [base, type, path, k, ki]
                                        index = self._KEY_SEPERATOR.join(keys)
                                        metadata_index.append(index)
                    
                    else:
                        keys = [base, type, path]
                        index = self._KEY_SEPERATOR.join(keys)
                        metadata_index.append(index)             
                            
        return metadata_index


    @classmethod
    def template_filter(cls, *args):

        key_sep = cls._KEY_SEPERATOR

        def filter(i:str)->bool:
            list_boolean = []

            for n in range(len(args)):
                try:
                    r = i.split(key_sep)[n].lower() == args[n].lower()
                except:
                    r = False
                list_boolean.append(r)

            return all(list_boolean)

        return filter


    def list_templates(self, base:str=None, type:str=None) -> t.List[str]:

        return self._index()
    
