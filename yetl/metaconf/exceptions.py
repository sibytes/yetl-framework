class ProjectVersionInvalid(Exception):
    def __init__(self, invalid_version: str, required_version: str):
        self.message = f"Invalid version {invalid_version}. API version should be {required_version}"
        super().__init__(self.message)


class ProjectDirectoryNotSet(Exception):
    def __init__(self):
        self.message = "A project path must be supplied providing a parameter for either an environment variable (project_path_variable) or a literal path (project_path)."
        super().__init__(self.message)


class ProjectDirectoryNotExists(Exception):
    def __init__(self, path):
        self.message = f"Project path {path} does not exist."
        super().__init__(self.message)