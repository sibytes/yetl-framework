from jinja2 import BaseLoader, TemplateNotFound, Environment, Undefined
from os.path import getmtime
import os
import typing as t
from collections import abc


import yaml
from collections import ChainMap


class Builder:

    _linked_index_resolvers = {
        "table_schema" : ["Dataset", "TableSchema"],
        "dataset": ["Dataset", "*"]
    }

    @classmethod
    def build(cls, searchpath:str, undefined: t.Type[Undefined] = Undefined) -> None:

        loader = FileMetasource(searchpath=searchpath)
        env = Environment(loader=loader, undefined=undefined)
        tpt_datastores = Builder._list_templates(env, "Datastore")

        for tpt_ds in tpt_datastores:
            ds = Builder._render(tpt_ds, env, loader)

            child_templates = dict(cls._linked_index_resolvers)
            for k, v in child_templates.items():
                if k in ds.keys():
                    try:
                        tpt = Builder._list_templates(env, *v, ds[k])[0]
                    except:
                        raise Exception(f"template for search for {v} can't be found")

                    child_templates[k] = Builder._render(tpt, env, loader)

        return child_templates
        # return [Builder._render(tpt, env, loader) for tpt in tpt_datastores]
            

    @classmethod
    def _render(cls, template_index:str, env:Environment, loader):
        template = env.get_template(template_index)
        rendered = template.render(loader.get_parameters(template_index))
        rendered_dict = yaml.safe_load(rendered)
        return rendered_dict

    @classmethod
    def _list_templates(cls, env:Environment, *args):
        return env.list_templates(
            filter_func=FileMetasource.template_filter(*args))



class FileMetasource(BaseLoader):

    _API_VESRION = "apiVersion"
    _API_NAMESPACE = "yetl-framework.io"
    _API_DEFAULT = "default"
    _INDEX_SEPARATOR = "!"
    _ENABLE_DICT_INDEX = ["Datastore"]

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
        """ Returns an inner dictionary from a dictionary using a list of list

            The list of keys can explicitly be a list or a character separated
            string where the separator is defined in self._INDEX_SEPARATOR.
        
        """
        if isinstance(index, str):
            index = index.split(self._INDEX_SEPARATOR)

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
            objects to be easily found. Ultimately this means that templates
            can be defined an isolated at lower grain than file which is useful
            to allow the metadata to be declared in a convenient way for the user
            but render in way that needed for the yetl.
            
            The index is in 2 parts:

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
        # walk the files in the template home dir
        for searchpath in self.searchpath:
            walk_dir = os.walk(searchpath, followlinks=self.followlinks)
            for dirpath, _, filenames in walk_dir:
                for filename in filenames:

                    # load yaml data from the file
                    metafile = os.path.join(dirpath, filename)

                    f = self._open_if_exists(metafile)
                    if f is None:
                        raise TemplateNotFound(metafile)
                    try:
                        metadata: dict = yaml.safe_load(f)
                    finally:
                        f.close()

                    # parse out the API, since we need it for part 1 of the index
                    try:
                        api_version = metadata[self._API_VESRION]
                    except KeyError as e:
                        raise Exception(
                            f"Invalid format {self._API_VESRION} not found", e
                        )

                    api_version = self._get_api_version(api_version)

                    # set variables for part 1 of the index
                    base = api_version["base"]
                    type = api_version["type"]
                    path = f"{dirpath}/{filename}"

                    if base in self._ENABLE_DICT_INDEX:
                        for k, v in metadata.items():
                            if isinstance(v, dict):
                                for ki, vi in v.items():
                                    if ki != self._API_DEFAULT and isinstance(vi, dict):
                                        # build part1 and part2 of the index and add the index
                                        keys = [base, type, path, k, ki]
                                        index = self._INDEX_SEPARATOR.join(keys)
                                        metadata_index.append(index)

                    else:
                        # build part1 of the index only
                        keys = [base, type, path]
                        index = self._INDEX_SEPARATOR.join(keys)
                        metadata_index.append(index)

        return metadata_index

    @classmethod
    def template_filter(cls, *args):
        """ Returns a filter index function for jinja template listing

            Returns a function that allows arguments to be passed in to
            filter a sub-set template indexes.

            e.g. we can call the following to return the 
            Datastore!Adls template indexes:

            templateEnv.list_templates(filter_func=FileMetasource.template_filter("Datastore", "Adls"))
        
        """
        key_sep = cls._INDEX_SEPARATOR

        def filter(i: str) -> bool:
            list_boolean = []

            for n in range(len(args)):
                try:
                    r = i.split(key_sep)[n].lower() == args[n].lower()
                    r = r or args[n] == "*"
                except:
                    r = False
                list_boolean.append(r)

            return all(list_boolean)

        return filter

    def list_templates(self, base: str = None, type: str = None) -> t.List[str]:
        """List the template indexes"""
        return self._index()

    def _get_source_dict(self, index: str):
        """ Given a template index return the content.

            The 1st part of the index is used to the return the file.
            The file is loaded and if there is a second part of the index
            this is used to return a subset or the contained dictionary.

            Once the dictionary is returned we must expand the defaults.
            Default in the templates allow object level defaults to be 
            declared which apply to the abbreviated objects that follow.
            This makes it very convenient for the users to create concise
            templates. However we need to do a bit of work to fill these
            defaults into the objects before we render the templates since
            some files contain multiple templates and we may only render
            the relevant templates and so the defaults need to be filled
            in before hand.
        
        """

        # split out the file index and dictationary key index
        file_index = index.split(self._INDEX_SEPARATOR)[:3]

        try:
            dict_index = index.split(self._INDEX_SEPARATOR)[3:]
        except:
            dict_index = None

        # load the data
        f = self._open_if_exists(file_index[2])
        try:
            data = yaml.safe_load(f)
        except:
            raise TemplateNotFound(file_index[2])
        finally:
            f.close()

        # parse out the API version, since we fill this into the defaults also
        # it's useful for serialising into an object api following template 
        # rendering
        try:
            api_version = data[self._API_VESRION]
        except KeyError as e:
            raise Exception(f"Invalid format {self._API_VESRION} not found", e)

        api_version = self._get_api_version(api_version)

        # expand out the defaults and api version type information
        data = self._expand_defaults(data, api_version)

        # finally if there is a dictionary index look
        # up the dictionary and return a subset of the file
        # as a template.
        if dict_index:
            try:
                data = self._lookup_index(data, dict_index)
            except:
                raise TemplateNotFound(index)

        return data

    def get_source(
        self, environment: Environment, template: str
    ) -> t.Tuple[str, str, t.Callable[[], bool]]:
        """
        
        """

        # Lookup the template using the template index.
        contents = self._get_source_dict(template)

        # dump out to yaml text
        class NoAliasDumper(yaml.Dumper):
            def ignore_aliases(self, data):
                return True

        contents: str = yaml.dump(contents, indent=4, Dumper=NoAliasDumper)

        filename = template.split(self._INDEX_SEPARATOR)[2]

        # TODO autoloading support.
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
