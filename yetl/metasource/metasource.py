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

        self.master_metadata = self._load()


    def _load(self):
        """
            Loads the metadata for a datafeed.

            This loads all of the metadata data files in to single dictionary.
            This is a step prior to applying jinja rendering.
        """
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

                    metadata, api_version = self._expand_defaults(metadata)

                    relative_path = dirpath.replace(searchpath, ".") + f"/{filename}"
                    self._index_metadata(master_metadata, metadata, api_version["base"], relative_path)

        # needs to done with jinja templating but in order
        # to move onto that it's easier if these are stictched
        # first.
        # TODO: refactor into a template render
        self._stitch_file_references(master_metadata)

        return master_metadata


    def _stitch_file_references(self, data:dict):

        datastores:dict = data["Datastore"]

        for k in datastores.keys():
            datastores_i:dict = datastores[k]["datastores"]

            for ki in datastores_i.keys():

                dataset_path = datastores_i[ki].get("dataset")
                if dataset_path:
                    try:
                        dataset = data["Dataset"][dataset_path]
                    except KeyError as e:
                        msg = f"Datastore {ki} Dataset with path reference {dataset_path} not found in Dataset metadata"
                        raise Exception(msg, e)

                    datastores_i[ki]["dataset"] = dataset["dataset"]

        del data["Dataset"]
                


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


    def _open_if_exists(self, filename: str, mode: str = "rb") -> t.Optional[t.IO]:
        """Returns a file descriptor for the filename if that file exists,
        otherwise ``None``.
        """
        if not os.path.isfile(filename):
            return None

        return open(filename, mode)


    def _expand_defaults(self, data: dict):

        defaulted_data = dict()
        try:
            api_version = data[self._API_VESRION]
        except KeyError as e:
            raise Exception(f"Invalid format {self._API_VESRION} not found", e)
        
        api_version = self._get_api_version(api_version)

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
                        if ki != self._API_DEFAULT or len(v.items())==1:
                            defaulted[ki] = dict(ChainMap(vi, default))
                    else:
                        defaulted[ki] = vi

                defaulted_data[k] = defaulted

            else:
                defaulted_data[self._API_VESRION] = api_version
                defaulted_data[k] = v


        # return the api version in tuple with collection
        # so we can index 
        return defaulted_data, api_version


    def _index_metadata(self, master:dict, metadata:dict, level1:str, level2:str):
        """
            takes a dictionary wraps it into a 2 level deep key dictionary
            and inserts it into the indexed master dictionary
        """

        base = master.get(level1)

        if base:
            base[level2] = metadata
        else:
            fileindex = {level2: metadata}
            master[level1] = fileindex

    def _get_source_dict(self, template: str):
        indexes = template.split(self._KEY_SEPERATOR)
        
        try:
            contents = self.master_metadata
            for i in indexes:
                contents = contents[i]

        except:
            raise TemplateNotFound(template)

        return contents


    def get_source(
        self, environment: Environment, template: str
    ) -> t.Tuple[str, str, t.Callable[[], bool]]:

        contents = self._get_source_dict(template)

        class NoAliasDumper(yaml.Dumper):
            def ignore_aliases(self, data):
                return True
                
        contents:str = yaml.dump(contents, indent=4, Dumper=NoAliasDumper)

        filename = template     

        def uptodate() -> bool:
            True
            # try:
            #     return os.path.getmtime(filename) == mtime
            # except OSError:
            #     return False      

        return contents, filename, uptodate

    def get_parameters(
        self, template: str
    ):

        contents = self._get_source_dict(template)
        contents["datastore"] = contents
        contents["table"] = {}
        return contents



    def list_templates(self) -> t.List[str]:
        templates = []
        for k, v in self.master_metadata.items():
            for ki in v.keys():
                if k != "Datastore":
                    key = f"{k}{self._KEY_SEPERATOR}{ki}" 
                    templates.append(key)
                else:
                    for kj in v[ki]["datastores"].keys():
                        keys = [k, ki, "datastores", kj]
                        key = self._KEY_SEPERATOR.join(keys)
                        templates.append(key)

        return templates

