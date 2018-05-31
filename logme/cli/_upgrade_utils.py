from typing import Union

from pathlib import Path
from copy import deepcopy

from bnmutils import ConfigParser

from ._cli_utils import get_color_tpl


NONLOGGER_CONFIGS = ['colors']


def upgrade_to_latest(config_path: Union[str, Path]):
    """
    upgrade the existing logme.ini file to latest version
    *Will write to existing file*

    :param config_path: logme.ini file
    """
    # config = read_config(config_path)
    config_dict = ConfigParser.from_files(config_path).to_dict()

    config_dict_updated = {}

    _upgrade_with_color_config(config_dict, config_dict_updated)

    for k, v in config_dict.items():
        if k not in NONLOGGER_CONFIGS:
            updated = _upgrade_logging_config_section(v)

            config_dict_updated[k] = updated

    new_conf = ConfigParser.from_dict(config_dict_updated)

    with open(config_path, 'w') as file:
        new_conf.write(file)


# TODO: add functionality to automatically figure out which version to update
def _upgrade_logging_config_section(config_dict: dict) -> dict:
    """
    -- v1.1.0 update --

    Upgrade the previous version of *individual config(ConfigParser section)* to latest
    
    :param config_dict: Dict of a config section content, *without the section key*

    :return: updated dict
    """
    latest = {}

    for k, val in config_dict.items():
        if isinstance(val, dict) and not val.get('type'):
            key = k.replace('Handler', '').lower()
            new_conf = {key: deepcopy(val)}
            new_conf[key]['type'] = k

            latest.update(new_conf)
        else:
            latest[k] = val

    return latest


def _upgrade_with_color_config(config_dict, config_dict_updated: dict):
    """
    -- v1.2.0 update --

    Upgrade the new config dict with color config.
    * This function updates the original 'config_dict_updated'*

    :param config_dict: the original config dictionary to be passed
    :param config_dict_updated: new config dict to be written to 'logme.ini' file
    """
    try:
        color_config = {'colors': config_dict['colors']}
    except KeyError:
        color_config = get_color_tpl()

    config_dict_updated.update(color_config)
