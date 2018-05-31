from pathlib import Path
from collections import defaultdict
from contextlib import contextmanager

from typing import Union

from bnmutils import ConfigParser
from ..exceptions import LogmeError
from ..utils import ensure_dir


@contextmanager
def ensure_conf_exist(project_root: str) -> Path:
    """
    Ensure logme.ini file exists, if it does, return the file path as pathlib.Path object,

    :param project_root: project_root where logme.ini is.
    :raises: LogmeError, if the configuration file does not exist

    :returns: logme.ini file path
    """

    logme_conf = Path(project_root) / 'logme.ini'

    if logme_conf.exists():
        yield logme_conf
    else:
        raise FileNotFoundError(f"log me config file does not exist in {Path.cwd()}, "
                                f"if you'd like to initialize logme in this directory, please type 'logme init'.")


def validate_conf(name: str, ini_file_path: Union[str, Path]):
    """
    Helper function for 'logme init' command,
    ensure the logger name passed in does not already exist in the ini file

    :param name: name of the section to be added
    :param ini_file_path: path of the logme.ini file
    """
    config = ConfigParser.from_files(ini_file_path)

    if config.has_section(name):
        raise LogmeError(f"'{name}' logging config already exists in config file: {ini_file_path}")
    elif not config.has_section('logme'):
        raise LogmeError(f"{ini_file_path} is not a valid logme.ini file")


def get_color_tpl() -> dict:
    """
    Get color template for logme.ini
    """
    color_config = {
        'CRITICAL': {'color': 'PURPLE', 'style': 'BOLD'},
        'ERROR': 'RED',
        'WARNING': 'YELLOW',
        'INFO': 'None',
        'DEBUG': 'GREEN',
    }

    return {'colors': color_config}


def get_tpl(name: str, **kwargs: str) -> dict:

    """
    Get the template dict for the logger configuration

    :param name: str, name of the logger
    :param kwargs: keys = ['level', 'formatter', 'filename']

    :return: dict
    """
    check_options(**kwargs)

    config = defaultdict(dict)

    logger_template = {
            'level': 'DEBUG',
            'formatter': None,
            'stream': {
                'type': 'StreamHandler',
                'active': True,
                'level': 'DEBUG',
            },
            'file': {
                'type': 'FileHandler',
                'active': False,
                'level': 'DEBUG',
                'filename': 'mylogpath/foo.log',
            },
            'null': {
                'type': 'NullHandler',
                'active': False,
                'level': 'NOTSET'
            },
        }

    map_template(logger_template, kwargs)

    config[name] = logger_template

    return dict(config)


def map_template(template: dict, input_: dict) -> None:
    """
    Update the template dict with the input, if input value exists

    *This updates the original dict passed in*

    :param template: dict
    :param input_: keys = ['level', 'formatter', 'filename']
    """
    for k, v in template.items():
        config_val = input_.get(k)

        if isinstance(v, dict) and v['type'] != 'NullHandler':
            map_template(v, input_)

        if config_val:
            template[k] = config_val.upper() if k == 'level' else config_val


def check_options(**kwargs):

    """
    check the level and log_path options passed, if the log_path doesn't exist, make the dir

    :param kwargs: keys = ['level', 'log_path']

    :raises: LogmeError, if invalid level passed
    """

    allowed_levels = ['critical', 'error', 'warning', 'info', 'debug', 'notset',
                      '50', '40', '30', '20', '10', '0']

    if kwargs.get('level') and kwargs['level'].lower() not in allowed_levels:
        raise LogmeError(f"{kwargs['level']} is not allowed, "
                         f"please specify the following: {allowed_levels}")

    # Make the directory and the log file
    if kwargs.get('filename'):
        ensure_dir(kwargs['filename'])

