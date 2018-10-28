from typing import Union

from pathlib import Path

from bnmutils import ConfigParser
from configparser import NoSectionError

from .exceptions import InvalidOption, LogmeError, InvalidLoggerConfig


def ensure_dir(dir_path: Union[Path, str], path_type: str='parent'):
    """
    Ensure the existence of the directory,

    :param dir_path: the path to be ensured
    :param path_type: current - ensure the passed in directory exists, typically used when


    """
    path_mapping = {
        'current': Path(dir_path).resolve(),
        'parent': Path(dir_path).parent.resolve()
    }

    try:
        dir_abs = path_mapping[path_type]

        if not dir_abs.exists():
            dir_abs.mkdir(parents=True, exist_ok=True)
    except KeyError:
        raise InvalidOption(f"{path_type} is not a valid option, please pass in either 'parent' or 'current'")


def check_scope(scope: str, options: list) -> bool:
    """
    check if the scope passed is within the options.
    Used both in logme/__init__.py and providers.LogDecorator

    """
    if scope not in options:
        raise LogmeError(f"scope '{scope}' is not supported, "
                         f"please use one of {options}")

    return True


# ---------------------------------------------------------------------------
# Utilities for getting configuration content
# ---------------------------------------------------------------------------
def get_logger_config(caller_file_path: Union[str, Path], name: str=None) -> dict:
    """
    Get logger config as dictionary

    :param caller_file_path: file path of the caller, __file__
    :param name: the name(section in logme.ini) of the config to be passed. (optional, default: 'logme')

    :return: logger configuration dictionary
    :raises: InvalidConfig, if name is not in config, or name == 'colors'
    """
    if name == 'colors':
        raise InvalidLoggerConfig(f"'colors' cannot be used as a logger configuration")

    if not name:
        name = 'logme'

    try:
        return get_config_content(caller_file_path, name=name)
    except NoSectionError:
        raise InvalidLoggerConfig(f"Invalid logger config '{name}'")


def get_color_config(caller_file_path: Union[str, Path]):
    """
    Return color configuration dict if 'colors' section exists, return None if not found
    """
    try:
        return get_config_content(caller_file_path, 'colors')
    except NoSectionError:
        return


def get_config_content(caller_file_path: Union[str, Path], name: str) -> dict:
    """
    Get the config section as a dictionary

    :param caller_file_path: file path of the caller, __file__
    :param name: the section name in an .ini file

    :return: configuration as dict
    """

    init_file_path = get_ini_file_path(caller_file_path)

    config = ConfigParser.from_files(init_file_path)

    try:
        return config.to_dict(section=name)
    except NoSectionError:
        raise NoSectionError(f"'{name}' is not a valid configuration in {init_file_path}")


def get_ini_file_path(caller_file_path: Union[str, Path]) -> Path:
    """
    Get the logme.ini config file path

    :param caller_file_path: file path of the caller, callable.__file__

    :return: Path object of the logme.ini
    """

    caller_file_path = Path(caller_file_path).resolve()
    if caller_file_path in [Path(caller_file_path.root).resolve(),
                            caller_file_path.home().resolve()]:
        raise ValueError(f"logme.ini does not exist, please use 'logme init' command in your project root.")

    conf_path = caller_file_path.parent / 'logme.ini'
    if not conf_path.exists():
        return get_ini_file_path(Path(caller_file_path).parent)
    else:
        return conf_path.resolve()
