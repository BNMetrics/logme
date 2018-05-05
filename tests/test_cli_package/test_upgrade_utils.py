import pytest

import shutil
from pathlib import Path

from logme.cli._upgrade_utils import _upgrade_config_section, upgrade_to_latest
from logme.config import read_config
from logme.utils import conf_to_dict

from .config_template import ver10_config, ver11_config


current_dir = Path(__file__).parent


def test_upgrade_to_latest(tmpdir):
    # Copy logme.ini to tmpdir
    logme_file = current_dir / 'logme.ini'
    tmp_logme = tmpdir.join('logme.ini')
    shutil.copyfile(logme_file, tmp_logme)

    upgrade_to_latest(tmp_logme)

    # Validate upgraded file
    config = read_config(tmp_logme)
    config_before = read_config(logme_file)

    assert config.sections() == config_before.sections()

    assert conf_to_dict(config.items('latest')) == \
           conf_to_dict(config_before.items('latest')) == \
           ver11_config

    for i in config.sections():
        conf_dict = conf_to_dict(config.items(i))

        for k, v in conf_dict.items():
            if isinstance(v, dict):
                assert v.get('type') is not None

            assert all(c.islower() for c in k)


@pytest.mark.parametrize('input_config',
                         [
                             pytest.param(ver10_config, id='upgrade from v1.0.*'),
                             pytest.param(ver11_config, id='Already new version, '
                                                           'output should not change'),
                         ])
def test_upgrade_config_section(input_config):
    upgraded = _upgrade_config_section(input_config)

    assert upgraded == ver11_config
