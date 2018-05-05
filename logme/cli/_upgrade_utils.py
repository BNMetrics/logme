from typing import Union

from pathlib import Path
from copy import deepcopy

from ..config import read_config
from ..utils import conf_to_dict, dict_to_config, flatten_config_dict


def upgrade_to_latest(config_path: Union[str, Path]):
    """
    upgrade the existing logme.ini file to latest version
    *Will write to existing file*

    :param config_path: logme.ini file
    """
    config = read_config(config_path)

    config_dict_updated = {}

    for i in config.sections():
        config_dict = conf_to_dict(config.items(i))
        updated = _upgrade_config_section(config_dict)

        config_dict_updated[i] = flatten_config_dict(updated)

    new_conf = dict_to_config(config_dict_updated)

    with open(config_path, 'w') as file:
        new_conf.write(file)


# TODO: add functionality to automatically figure out which version to update
def _upgrade_config_section(config_dict: dict) -> dict:
    """
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
