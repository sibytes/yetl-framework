
from jinja2 import BaseLoader, TemplateNotFound, Environment, Undefined
from os.path import getmtime
import os
import typing as t
from ..logging import get_logger


import yaml

logger = get_logger(__name__)


class Index():

    _API_VESRION = "apiVersion"
    _API_NAMESPACE = "yetl-framework.io"
    _API_DEFAULT = "default"
    _INDEX_SEPARATOR = "!"
    _ENABLE_DICT_INDEX_BASES = ["Datastore", "Dataset"]
    _DISABLE_DICT_INDEX_TYPES = ["TableSchema"]
    _ENABLE_DEFAULT = ["Dataset"]

    def _lookup_index(self, data: dict, index: t.Union[str, list]):
        """Returns an inner dictionary from a dictionary using a list of list

        The list of keys can explicitly be a list or a character separated
        string where the separator is defined in self._INDEX_SEPARATOR.

        """
        if isinstance(index, str):
            index = index.split(self._INDEX_SEPARATOR)

        n = data
        for k in index:
            n = n[k]

        return n


    def _index(self):
        """Indexes the templates so that component parts
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

                    if base in self._ENABLE_DICT_INDEX_BASES and (
                        type not in self._DISABLE_DICT_INDEX_TYPES
                    ):
                        for k, v in metadata.items():
                            if isinstance(v, dict):
                                for ki, vi in v.items():
                                    # if it's not a default and a dictionary
                                    # or defaults are enabled.
                                    if (
                                        ki != self._API_DEFAULT
                                        or base in self._ENABLE_DEFAULT
                                    ) and isinstance(vi, dict):
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
        """Returns a filter index function for jinja template listing

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



    def get_source_dict(self, index: str):
        """Given a template index return the content.

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
