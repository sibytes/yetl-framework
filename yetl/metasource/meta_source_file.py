from jinja2 import BaseLoader, TemplateNotFound, Environment
from os.path import join, exists, getmtime
import os
import typing as t
from collections import abc



class MetasourceFile(BaseLoader):


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

    def get_source(
        self, environment: Environment, template: str
    ) -> t.Tuple[str, str, t.Callable[[], bool]]:
        pieces = self._split_template_path(template)
        for searchpath in self.searchpath:
            filename = os.path.join(searchpath, *pieces)
            f = self._open_if_exists(filename)
            if f is None:
                continue
            try:
                contents = f.read().decode(self.encoding)
            finally:
                f.close()

            mtime = os.path.getmtime(filename)

            def uptodate() -> bool:
                try:
                    return os.path.getmtime(filename) == mtime
                except OSError:
                    return False

            return contents, filename, uptodate
        raise TemplateNotFound(template)

    def list_templates(self) -> t.List[str]:
        found = set()
        for searchpath in self.searchpath:
            walk_dir = os.walk(searchpath, followlinks=self.followlinks)
            for dirpath, _, filenames in walk_dir:
                for filename in filenames:
                    template = (
                        os.path.join(dirpath, filename)[len(searchpath) :]
                        .strip(os.path.sep)
                        .replace(os.path.sep, "/")
                    )
                    if template[:2] == "./":
                        template = template[2:]
                    if template not in found:
                        found.add(template)
        return sorted(found)

    def _split_template_path(self, template: str) -> t.List[str]:
        """Split a path into segments and perform a sanity check.  If it detects
        '..' in the path it will raise a `TemplateNotFound` error.
        """
        pieces = []
        for piece in template.split("/"):
            if (
                os.path.sep in piece
                or (os.path.altsep and os.path.altsep in piece)
                or piece == os.path.pardir
            ):
                raise TemplateNotFound(template)
            elif piece and piece != ".":
                pieces.append(piece)
        return pieces

    def _open_if_exists(self, filename: str, mode: str = "rb") -> t.Optional[t.IO]:
        """Returns a file descriptor for the filename if that file exists,
        otherwise ``None``.
        """
        if not os.path.isfile(filename):
            return None

        return open(filename, mode)