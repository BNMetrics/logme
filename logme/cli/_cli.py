import click

from pathlib import Path

from bnmutils import ConfigParser

from ..exceptions import LogmeError
from ..__version__ import __version__

from ._cli_utils import ensure_conf_exist, validate_conf, get_tpl, get_color_tpl
from ._upgrade_utils import upgrade_to_latest

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
                             help='the filename where you want to store your log',
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


@click.version_option(__version__, '--version', '-v', '-V')
@click.group(context_settings={'help_option_names': ['-h', '--help']})
def cli():
    """
    *entry point*

    Simple init:

        >>> logme init

    To make a new log config file in specified dir:

        >>> logme init -p /var/workspace/my_project -mk

    Make a new logger config in existing config file:

        >>> logme add my_logger

    """


@cli.command()
@click.option('--mkdir', '-mk',
              help='Create the directory in which logme.ini resides.',
              is_flag=True)
@click.option('--override', '-o',
              help='Use this flag to override the current logme.ini file',
              is_flag=True)
@add_options()
@click.pass_context
def init(ctx, project_root, override, mkdir, level, formatter, log_path):
    """
    Entry point.

    Command to set up a logme config file with master logger configuration

    """
    conf_content = get_color_tpl()
    master_logging_config = get_tpl('logme', level=level,
                                    formatter=formatter, filename=log_path)
    conf_content.update(master_logging_config)

    config = ConfigParser.from_dict(conf_content)

    abs_path = Path(project_root).resolve()
    conf_location = abs_path.joinpath('logme.ini')

    if not abs_path.exists():
        if not mkdir:
            raise NotADirectoryError(f"{abs_path.parent.resolve() / project_root} does not exist. If you'd "
                                     f"like to make the directory, please use '-mk' flag.")
        else:
            abs_path.mkdir(parents=True, exist_ok=True)

    if conf_location.exists() and not override:
        raise LogmeError(f"logme.ini already exists at {conf_location}")

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

        # check if section already exist
        validate_conf(name, logme_conf)

        conf_content = get_tpl(name, level=level, formatter=formatter, filename=log_path)
        config = ConfigParser.from_dict(conf_content)

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
    none_removables = {
        'logme': "'logme' master configuration cannot be removed!",
        'colors': "'colors' configuration cannot be removed! To remove color "
                  "logging, set all color values to 'None'",
    }

    if none_removables.get(name):
        raise LogmeError(none_removables[name])

    with ensure_conf_exist(project_root) as logme_conf:

        config = ConfigParser.from_files(logme_conf)
        config.remove_section(name)

        with logme_conf.open('w+') as conf:
            config.write(conf)


@cli.command()
@add_options(['project_root'])
@click.pass_context
def upgrade(ctx, project_root):
    """
    Command for updating the current log file to newest version, v1.0 -> v 1.1.0+
    """
    with ensure_conf_exist(project_root) as logme_conf:
        upgrade_to_latest(logme_conf)

    print(f"{logme_conf.resolve()} has been updated to {__version__}")
