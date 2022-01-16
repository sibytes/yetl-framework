
from jinja2 import Environment, Undefined
import typing as t
from .logging import get_logger
from .metasource import (FileMetasource, Index)
import yaml

logger = get_logger(__name__)

class Builder:

    _linked_index_resolvers = {
        "table_schema": ["Dataset", "TableSchema"],
        "dataset": ["Dataset", "*"],
    }

    @classmethod
    def build(cls, searchpath: str, undefined: t.Type[Undefined] = Undefined) -> None:

        loader = FileMetasource(searchpath=searchpath)
        env = Environment(loader=loader, undefined=undefined)
        i_datastores = Builder._list_templates(env, "Datastore")
        tpt_datastores = Builder._list_templates(env)
        import pprint

        pprint.pprint(tpt_datastores)

        docs = []

        for i_ds in i_datastores:
            table_schema: dict = None
            dataset: dict = None

            datastore_params = loader.get_source_dict(i_ds)
            ds = cls._render(i_ds, env, datastore_params)

            dataset_idx = Builder._get_linked_index(ds, "dataset", env, loader)
            del ds["dataset"]
            # # dataset = loader.get_source_dict(index)
            dataset_params = {"datastore": ds}
            table_schema_idx = Builder._get_linked_index(
                ds, "table_schema", env, loader
            )
            # if there is a table schema then render a metadoc for every table
            
            if table_schema_idx:
                del ds["table_schema"]
                table_schema = loader.get_source_dict(table_schema_idx)

                for table, schema in table_schema["dataset"].items():

                    schema["name"] = table
                    dataset_params["table"] = schema
                    
                    metadoc = {"datastore": ds}
                    try:
                        rendered_dataset = Builder._render(
                            dataset_idx, env, dataset_params
                        )
                    except:
                        rendered_dataset = loader.get_source_dict(dataset_idx)

                    metadoc["table_schema"] = schema
                    metadoc["dataset"] = rendered_dataset

                    docs.append(metadoc)
            # if there is no table schema then we're not metadata driving the dataset
            # in this case it's handle generically or it delcared specifically.
            else:
                metadoc = {"datastore": ds}
                try:
                    rendered_dataset = Builder._render(dataset_idx, env, dataset_params)
                except:
                    rendered_dataset = loader.get_source_dict(dataset_idx)
                    metadoc["dataset"] = rendered_dataset
                docs.append(metadoc)

        #     ds = Builder._render(tpt_ds, env, loader.get_parameters(tpt_ds))
        return docs

    @classmethod
    def _get_linked_index(
        cls, datastore: dict, resolver: str, env: Environment, loader: FileMetasource
    ) -> dict:

        lkup = cls._linked_index_resolvers[resolver]

        dict_index = None
        path = datastore.get(resolver)
        if path:
            dict_index = path.split(FileMetasource._INDEX_SEPARATOR)
            if len(dict_index) > 1:
                dict_index = [dict_index[0], resolver] + dict_index[1::]
            elif lkup[1] not in FileMetasource._DISABLE_DICT_INDEX_TYPES:
                dict_index = [dict_index[0], resolver, FileMetasource._API_DEFAULT]

        # search for a template <type>!<sub_type>!<path>![<dict_path>]
        if dict_index:
            templates = Builder._list_templates(env, *lkup, *dict_index)

            if len(templates) == 0:
                raise Exception(
                    f"template for search for {lkup} can't be found. The the path {path} is correct."
                )
            elif len(templates) > 1:
                raise Exception(
                    f"template for search for {lkup} found more than one, index not unique"
                )

            i_template = templates[0]

            return i_template
        else:
            return None

    @classmethod
    def _render(
        cls, template_index: str, env: Environment, parameters: dict = {}
    ) -> dict:
        logger.debug(f"Rendering template: {template_index}")
        template = env.get_template(template_index)
        rendered = template.render(parameters)
        logger.debug(f"Rendered Template: \n {rendered}")
        rendered_dict: dict = yaml.safe_load(rendered)
        return rendered_dict

    @classmethod
    def _list_templates(cls, env: Environment, *args):
        return env.list_templates(filter_func=Index.template_filter(*args))
