from jinja2 import BaseLoader, TemplateNotFound, Environment, Undefined
from os.path import join, exists, getmtime
import os
import typing as t
from collections import abc

from jinja2.environment import *
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

    def _expand_defaults(self, data: dict, api_version: dict):

        defaulted_data = dict()

        for k, v in data.items():

            if k == self._API_VESRION:
                continue

            if isinstance(v, dict):
                default = v.get(self._API_DEFAULT, None)
                if not default:
                    default = {}
                default[self._API_VESRION] = api_version
                defaulted = {}

                for ki, vi in v.items():
                    if isinstance(vi, dict):
                        if ki != self._API_DEFAULT or len(v.items()) == 1:
                            defaulted[ki] = dict(ChainMap(vi, default))
                    else:
                        defaulted[ki] = vi

                defaulted_data[k] = defaulted

            else:
                defaulted_data[self._API_VESRION] = api_version
                defaulted_data[k] = v

        # return the api version in tuple with collection
        # so we can index
        return defaulted_data

    def _get_api_version(self, api_version_uri: str):

        # TODO: Need a better validator, probably a regex
        if api_version_uri.startswith(f"{self._API_NAMESPACE}/"):
            p = api_version_uri.split("/")
            if int(p[1]) != 1 or len(p) != 4:
                raise Exception(f"invalid {self._API_VESRION} uri version")

            api_version = {
                "namespace": p[0],
                "version": p[1],
                "base": p[2],
                "type": p[3],
            }
            return api_version
        else:
            raise Exception(f"invalid {self._API_VESRION} uri")

    def _lookup_index(self, data: dict, index: t.Union[str, list]):

        if isinstance(index, str):
            index = index.split("!")

        n = data
        for k in index:
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
        """ Indexes the templates so that component parts
            of a pipeline can be easily found.

            Metadata is organised for the convenience of the user. This
            means we have a bit work to do to peice things together for
            templating. This procedure creates an index that allows component
            objects to be easily found. The index is in 2 parts:

            Part 1:
                base_type!type!filepath
                
                Part 1 is mandatory and makes it easy to find the file for 
                certain types of objects. Not that objects are defined in 
                the file yaml description using apiVersion property. For example:

                    Dataset!Deltalake!./project/dataset/mydataset.yml

            Part 2:
                level_1_dict_key!level_2_dict_key!... and so on

                Part 2 is option and is dictionary key path to the object
                of concern with the template. This allows many objects
                to make use of defaults in a yaml definition but are
                in fact separate objects. Yaml definitions will only have
                intradocument key indexes where it makes sense e.g. datastore.

                    datastores!my_datastore

            Final example being:

                Dataset!Deltalake!./project/dataset/mydataset.yml!datastores!my_datastore



        
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
                        metadata: dict = yaml.safe_load(f)
                    finally:
                        f.close()

                    try:
                        api_version = metadata[self._API_VESRION]
                    except KeyError as e:
                        raise Exception(
                            f"Invalid format {self._API_VESRION} not found", e
                        )

                    api_version = self._get_api_version(api_version)
                    base = api_version["base"]
                    type = api_version["type"]
                    path = f"{dirpath}/{filename}"

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

        def filter(i: str) -> bool:
            list_boolean = []

            for n in range(len(args)):
                try:
                    r = i.split(key_sep)[n].lower() == args[n].lower()
                except:
                    r = False
                list_boolean.append(r)

            return all(list_boolean)

        return filter

    def list_templates(self, base: str = None, type: str = None) -> t.List[str]:

        return self._index()

    def _get_source_dict(self, index: str):

        file_index = index.split(self._KEY_SEPERATOR)[:3]

        try:
            dict_index = index.split(self._KEY_SEPERATOR)[3:]
        except:
            dict_index = None

        f = self._open_if_exists(file_index[2])
        try:
            data = yaml.safe_load(f)
        finally:
            f.close()

        try:
            api_version = data[self._API_VESRION]
        except KeyError as e:
            raise Exception(f"Invalid format {self._API_VESRION} not found", e)

        api_version = self._get_api_version(api_version)

        data = self._expand_defaults(data, api_version)

        if dict_index:
            data = self._lookup_index(data, dict_index)

        return data

    def get_source(
        self, environment: Environment, template: str
    ) -> t.Tuple[str, str, t.Callable[[], bool]]:

        contents = self._get_source_dict(template)

        class NoAliasDumper(yaml.Dumper):
            def ignore_aliases(self, data):
                return True

        contents: str = yaml.dump(contents, indent=4, Dumper=NoAliasDumper)

        filename = template

        def uptodate() -> bool:
            True
            # try:
            #     return os.path.getmtime(filename) == mtime
            # except OSError:
            #     return False

        return contents, filename, uptodate

    def get_parameters(self, template: str):

        contents = self._get_source_dict(template)
        contents["datastore"] = contents
        contents["table"] = {}
        return contents
