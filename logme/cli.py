import click

from pathlib import Path
from contextlib import contextmanager
from collections import defaultdict
from configparser import ConfigParser

from .exceptions import LogmeError
from .utils import dict_to_conf
from .config import read_config

_command_options = {
    'project_root': click.option('--project-root', '-p',
                                 help='The project root, where the logme.ini is, or where you want to place it. '
                                      'Relative/absolute path',
                                 default='.'),
    'level': click.option('--level', '-lvl',
                          help='the logging level',
                          default='DEBUG'),
    'formatter': click.option('--formatter', '-f',
                              help='the logging formatter',
                              default='{asctime} - {name} - {levelname} - {message}'),
    'log_path': click.option('--log-path', '-lp',
                             help='the directory where you want to store your log file, '
                                  'the log file will be named as *logger_name.log*',
                             default=None),
}


def add_options(options: list=None):

    """
    *decorator*

    Combining _command_options as one single decorator,

    - options can be passed to specify which option to use
    - if option is not specified, it will combine all the option

    """

    def add_options_wrapper(command_func):
        if not options:
            for option in _command_options.values():
                command_func = option(command_func)
        else:
            for option in options:
                command_func = _command_options[option](command_func)

        return command_func

    return add_options_wrapper


@click.group(context_settings={'help_option_names': ['-h', '--help']})
def cli():
    """
    *entry point*

    Simple init:

        >>> logme init

    To make a new log config file in specified dir:

        >>> logme init -p /var/workspace/my_project -mk

    Make a new logger config in existing config file:

        >>> logme logger my_logger

    """


@cli.command()
@click.option('--mkdir', '-mk',
              help='Create the directory in which logme.ini resides.',
              is_flag=True)
@add_options()
@click.pass_context
def init(ctx, project_root, mkdir, level, formatter, log_path):
    """
    Entry point.

    Command to set up a logme config file with master logger configuration

    """
    conf_content = get_tpl('logme', level=level, formatter=formatter, log_path=log_path)

    config = get_config(conf_content)

    abs_path = Path(project_root).resolve()
    conf_location = abs_path.joinpath('logme.ini')

    if not abs_path.exists():
        if not mkdir:
            raise NotADirectoryError(f"{abs_path.parent.resolve() / project_root} does not exist. If you'd "
                                     f"like to make the directory, please use '-mk' flag.")
        else:
            abs_path.mkdir(parents=True, exist_ok=True)

    with conf_location.open('w') as conf:
        config.write(conf)


@cli.command()
@click.argument('name', required=1)
@add_options()
@click.pass_context
def add(ctx, project_root, name, level, formatter, log_path):
    """
    Command for adding a logger configuration in a logme.ini file. Assuming logme.ini exists
    """
    with ensure_conf_exist(project_root) as logme_conf:

        validate_conf(name, logme_conf)

        conf_content = get_tpl(name, level=level, formatter=formatter, log_path=log_path)
        config = get_config(conf_content)

        # check if section already exist
        with logme_conf.open('a') as conf:
            config.write(conf)


@cli.command()
@click.argument('name', required=1)
@add_options(['project_root'])
@click.pass_context
def remove(ctx, name, project_root):
    """
    Command for removing a logger configuration in a logme.ini file.
    logme configuration cannot be removed
    """

    if name == 'logme':
        raise LogmeError("'logme' master logger configuration cannot be removed!")

    with ensure_conf_exist(project_root) as logme_conf:

        config = read_config(logme_conf)
        config.remove_section(name)

        with logme_conf.open('w+') as conf:
            config.write(conf)


@contextmanager
def ensure_conf_exist(project_root: str) -> Path:
    """
    Ensure logme.ini file exists, if it does, return the file path as pathlib.Path object,

    :param project_root: project_root where logme.ini is.
    :raises: LogmeError, if the configuration file does not exist
    """

    logme_conf = Path(project_root) / 'logme.ini'

    if logme_conf.exists():
        yield logme_conf
    else:
        raise FileNotFoundError(f"log me config file does not exist in {Path.cwd()}, "
                                f"if you'd like to initialize logme in this directory, please type 'logme init'.")


def validate_conf(name, ini_file_path):
    """
    Helper function for 'logme logger' command,
    ensure the logger name passed in does not already exist in the ini file

    :param name:
    :param ini_file_path:
    :return:
    """
    sections = read_config(ini_file_path).sections()

    if name in sections:
        raise LogmeError(f"'{name}' logging config already exists in config file: {ini_file_path}")
    elif 'logme' not in sections:
        raise LogmeError(f"{ini_file_path} is not a valid logme.ini file")


def get_config(conf_content: dict) -> ConfigParser:
    """

    :param conf_content: nested dict

    :return: configpaser.Configparser
    """
    config = ConfigParser()
    # preserve casing
    config.optionxform = str

    for k, v in conf_content.items():
        config[k] = v

    return config


def get_tpl(name: str, **kwargs: str) -> dict:

    """
    Get the template dict for the logger configuration

    :param name: str, name of the logger
    :param kwargs: keys = ['level', 'formatter', 'log_path']

    :return: dict
    """

    check_options(**kwargs)

    config = defaultdict(dict)

    logger_template = {
            'level': 'DEBUG',
            'formatter': None,
            'StreamHandler': {
                'level': 'DEBUG',
            },
            'FileHandler': {
                'level': 'DEBUG',
                'log_path': None,
            },
            'NullHandler': {
                'level': 'NOTSET'
            },
        }

    map_template(logger_template, kwargs)

    # flatten config dictionary
    config[name] = dict(dict_to_conf(logger_template))

    return dict(config)


def map_template(template: dict, input_: dict) -> None:
    """
    Update the template dict with the input, if input value exists

    *This updates the original dict passed in*

    :param template: dict
    :param input_: keys = ['level', 'formatter', 'log_path']
    """
    for k, v in template.items():
        config_val = input_.get(k)

        if isinstance(v, dict) and k != 'NullHandler':
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
    if kwargs.get('log_path'):
        log_path_abs = Path(kwargs['log_path']).resolve()
        if not log_path_abs.exists():
            log_path_abs.mkdir(parents=True, exist_ok=True)

