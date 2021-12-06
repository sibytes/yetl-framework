from jinja2 import BaseLoader, TemplateNotFound, Environment
from os.path import join, exists, getmtime
import os
import typing as t
from collections import abc
from abc import ABC, abstractmethod
import yaml
from collections import ChainMap

class Metasource(ABC):
    pass

    def _get_api_version(self, api_version_uri:str):

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

    def _open_if_exists(self, filename: str, mode: str = "rb") -> t.Optional[t.IO]:
        """Returns a file descriptor for the filename if that file exists,
        otherwise ``None``.
        """
        if not os.path.isfile(filename):
            return None

        return open(filename, mode)

    def _expand_defaults(self, data: dict):

        data_defaulted = dict()
        for k, v in data.items():

            if k == "apiVersion":
                api_version = self._get_api_version(v)

            # if it's a typed list with defaults
            if isinstance(v, list):

                try:
                    default = next(i for i in v if i["id"] == "default")
                except StopIteration:
                    continue
                except KeyError:
                    continue

                if default:
                    # might want this here not sure yet
                    # default["apiVersion"] = api_version
                    defaulted = list()
                    for i in v:

                        if i["id"] != "default":
                            # merge in defaults
                            n = dict(ChainMap(i, default))
                            defaulted.append(n)

                    data_defaulted[k] = defaulted
        
        # if not a typed list with defaults
        # just upack the api version
        if not data_defaulted and api_version:
            data_defaulted = data
        
        data_defaulted["apiVersion"] = api_version

        return data_defaulted


    def _key_by_api_version(self, master:dict, metadata:dict):

        api_version:dict = metadata["apiVersion"]
        del metadata["apiVersion"]

        master[api_version["base"]] = {
            api_version["type"] : metadata
        }



class FileMetasource(Metasource):

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

        self.master_metadata = self._load()


    def _load(self):

        master_metadata = dict()

        for searchpath in self.searchpath:
            walk_dir = os.walk(searchpath, followlinks=self.followlinks)
            for dirpath, _, filenames in walk_dir:
                for filename in filenames:
                    metafile = os.path.join(dirpath, filename)

                    f = self._open_if_exists(metafile)
                    if f is None:
                        continue
                    try:
                        metadata = yaml.safe_load(f)
                    finally:
                        f.close()

                    metadata = self._expand_defaults(metadata)

                    self._key_by_api_version(master_metadata, metadata)

        return master_metadata





# class _MetasourceFile(BaseLoader):


#     def __init__(
#         self,
#         searchpath: t.Union[str, os.PathLike, t.Sequence[t.Union[str, os.PathLike]]],
#         encoding: str = "utf-8",
#         followlinks: bool = False,
#     ) -> None:
#         """

#             Here we need to stitch the usability templates together into the jinja templates
#             that we want to render.
        
#         """
#         if not isinstance(searchpath, abc.Iterable) or isinstance(searchpath, str):
#             searchpath = [searchpath]

#         self.searchpath = [os.fspath(p) for p in searchpath]
#         self.encoding = encoding
#         self.followlinks = followlinks

#     def get_source(
#         self, environment: Environment, template: str
#     ) -> t.Tuple[str, str, t.Callable[[], bool]]:
#         pieces = self._split_template_path(template)
#         for searchpath in self.searchpath:
#             filename = os.path.join(searchpath, *pieces)
#             f = self._open_if_exists(filename)
#             if f is None:
#                 continue
#             try:
#                 contents = f.read().decode(self.encoding)
#             finally:
#                 f.close()

#             mtime = os.path.getmtime(filename)

#             def uptodate() -> bool:
#                 try:
#                     return os.path.getmtime(filename) == mtime
#                 except OSError:
#                     return False

#             return contents, filename, uptodate
#         raise TemplateNotFound(template)

#     def list_templates(self) -> t.List[str]:
#         found = set()
#         for searchpath in self.searchpath:
#             walk_dir = os.walk(searchpath, followlinks=self.followlinks)
#             for dirpath, _, filenames in walk_dir:
#                 for filename in filenames:
#                     template = (
#                         os.path.join(dirpath, filename)[len(searchpath) :]
#                         .strip(os.path.sep)
#                         .replace(os.path.sep, "/")
#                     )
#                     if template[:2] == "./":
#                         template = template[2:]
#                     if template not in found:
#                         found.add(template)
#         return sorted(found)

#     def _split_template_path(self, template: str) -> t.List[str]:
#         """Split a path into segments and perform a sanity check.  If it detects
#         '..' in the path it will raise a `TemplateNotFound` error.
#         """
#         pieces = []
#         for piece in template.split("/"):
#             if (
#                 os.path.sep in piece
#                 or (os.path.altsep and os.path.altsep in piece)
#                 or piece == os.path.pardir
#             ):
#                 raise TemplateNotFound(template)
#             elif piece and piece != ".":
#                 pieces.append(piece)
#         return pieces

