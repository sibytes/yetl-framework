import logging
import logging.config
import yaml


def getLogger(name: str, directoryPath: str = ".") -> logging:

    with open(f"{directoryPath}/logging.yml", "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    return logging.getLogger(name)