from pathlib import Path
from configparser import ConfigParser

from typing import Union

from .exceptions import InvalidConfig


# TODO: Rewrite!!!
def get_config_content(decorated_file_path):
    # return {
    #     'level': 'INFO',
    #     'formatter': '{levelname}: {asctime} - {name} - {module}::{funcName} - {message}',
    #     'file': '/path/to/my/file.ini',
    #     'StreamHandler': True
    # }

    init_file_path = get_ini_file_path(decorated_file_path)

    config = read_config(init_file_path)
    print(dict(config.items('logme')))
    return dict(config.items('logme'))


def read_config(file_path: Union[str, Path]) -> ConfigParser:
    """
    Read the config file given a file path,
    :param file_path: the file path which the ini file is located

    :return: ConfigParser object with section populated
    :raises: InvalidConfig, If file *does not exist* or if file is *empty*
    """
    config = ConfigParser()
    config.optionxform = str

    config.read(file_path)

    if not config.sections():
        raise InvalidConfig(f"{file_path} is not a valid config file.")

    return config


def get_ini_file_path(caller_file_path: Union[str, Path]) -> Path:
    """
    Get the logme.ini config file path

    :param caller_file_path: file path of the caller, callable.__name__

    :return: Path object of the logme.ini
    """
    conf_path = Path(caller_file_path).parent / 'logme.ini'

    if caller_file_path == Path('/').resolve():
        raise ValueError("logme.ini does not exist, please use 'logme init' command in your project root")

    if not conf_path.exists():
        return get_ini_file_path(Path(caller_file_path).parent)
    else:
        return conf_path.resolve()