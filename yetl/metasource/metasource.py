
from jinja2 import BaseLoader, TemplateNotFound, Environment, Undefined
from os.path import getmtime
import os
import typing as t
from collections import abc
from ..logging import get_logger
from .index import Index

import yaml
from collections import ChainMap

logger = get_logger(__name__)


class FileMetasource(BaseLoader, Index):

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
                base = api_version["base"]

                for ki, vi in v.items():
                    if isinstance(vi, dict):

                        if (
                            ki != self._API_DEFAULT
                            or base in self._ENABLE_DEFAULT
                            or len(v.items()) == 1
                        ):
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


    def _open_if_exists(self, filename: str, mode: str = "rb") -> t.Optional[t.IO]:
        """Returns a file descriptor for the filename if that file exists,
        otherwise ``None``.
        """
        if not os.path.isfile(filename):
            return None

        return open(filename, mode)


    def list_templates(self, base: str = None, type: str = None) -> t.List[str]:
        """List the template indexes"""
        return self._index()


    def get_source(
        self, environment: Environment, template: str
    ) -> t.Tuple[str, str, t.Callable[[], bool]]:
        """ """

        # Lookup the template using the template index.
        contents = self.get_source_dict(template)

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

