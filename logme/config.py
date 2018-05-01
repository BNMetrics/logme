from pathlib import Path
from configparser import ConfigParser, NoSectionError

from typing import Union

from .utils import conf_to_dict
from .exceptions import InvalidConfig


def get_config_content(caller_file_path: Union[str, Path], name: str=None) -> dict:
    """
    Get the config section as a dictionary

    :param caller_file_path: file path of the caller, __file__
    :param name: the name(section in logme.ini) of the config to be passed. (optional, default: 'logme')

    :return: logger configuration dictionary
    """

    init_file_path = get_ini_file_path(caller_file_path)

    config = read_config(init_file_path)

    try:
        if name:
            conf_section = config.items(name)
        else:
            conf_section = config.items('logme')

        return conf_to_dict(conf_section)
    except NoSectionError:
        raise InvalidConfig(f"'{name}' is not a valid configuration in {init_file_path}")


def read_config(file_path: Union[str, Path]) -> ConfigParser:
    """
    Read the config file given a file path,
    :param file_path: the file path which the ini file is located

    :return: ConfigParser object with section populated
    :raises: InvalidConfig, If file *does not exist* or if file is *empty*
    """
    config = ConfigParser()
    config.optionxform = str

    # Update on config.read on string format file_path to work with older version of python, e.g. 3.6.0
    config.read(str(file_path))

    if not config.sections():
        raise InvalidConfig(f"{file_path} is not a valid config file.")

    return config


def get_ini_file_path(caller_file_path: Union[str, Path]) -> Path:
    """
    Get the logme.ini config file path

    :param caller_file_path: file path of the caller, callable.__file__

    :return: Path object of the logme.ini
    """
    conf_path = Path(caller_file_path).parent / 'logme.ini'

    if caller_file_path in [Path(Path(caller_file_path).root).resolve(),
                            Path(caller_file_path).home().resolve()]:
        raise ValueError(f"logme.ini does not exist, please use 'logme init' command in your project root.")

    if not conf_path.exists():
        return get_ini_file_path(Path(caller_file_path).parent)
    else:
        return conf_path.resolve()
