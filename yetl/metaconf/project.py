import os
from logging import getLogger
import yaml
from .exceptions import (
    ProjectDirectoryNotSet,
    ProjectDirectoryNotExists
)


class Project:
    
    def __init__(
        self,
        project_path: str,
        project_path_is_variable: bool
    ):

        logger = getLogger( __name__)
        logger.info(f"building project path={project_path}, path_is_variable={project_path_is_variable}")

        self.directory = self._get_source_directory(
            project_path, project_path_is_variable
        )
        self.project_file_path = os.path.join(self.directory, "project.yml")

        project_dict = self._load_project()

        logger.info(project_dict)



    def _get_source_directory(
        self, project_path: str, project_path_is_variable: bool
    ):

        """Validate and the project directory property.
        Sets the project directory validating that either a valid path has been provided
        or an environment variable name that holds the path
        """

        if not project_path:
            raise ProjectDirectoryNotSet()

        if project_path_is_variable:
            directory = os.getenv(project_path)
        else:
            directory = project_path

        if not directory:
            raise ProjectDirectoryNotSet()

        if directory and not os.path.exists(directory):

            raise ProjectDirectoryNotExists(directory)

        directory = os.path.abspath(directory)
        return directory


    def _load_project(self):

        with open(self.project_file_path, "r") as f:
            project_dict = yaml.safe_load(f)

        return project_dict