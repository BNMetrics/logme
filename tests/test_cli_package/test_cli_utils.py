import pytest

from pathlib import Path
from click.testing import CliRunner

from bnmutils.novelty import cd

from logme import cli
from logme.exceptions import LogmeError

from logme.cli._cli_utils import (ensure_conf_exist, validate_conf, get_tpl,
                                  map_template, check_options, get_color_tpl)


def test_ensure_conf_exist(tmpdir, capsys):
    file_path = tmpdir.join('logme.ini')
    file_path.open('w').close()

    with ensure_conf_exist(tmpdir):
        print('conf_exists!')

    out, err = capsys.readouterr()

    assert out == 'conf_exists!\n'
    assert err == ''


def test_ensure_conf_exist_raise(tmpdir):
    with pytest.raises(FileNotFoundError):
        with ensure_conf_exist(tmpdir):
            pass


def test_validate_conf_section_exist(tmpdir):
    """ Test raise when section already exists"""
    with cd(tmpdir):
        runner = CliRunner()

        runner.invoke(cli, ['init'])
        runner.invoke(cli, ['add', 'blah'])

        with pytest.raises(LogmeError) as e_info:
            validate_conf('blah', Path(tmpdir / 'logme.ini'))

        assert "'blah' logging config already exists in config file" in e_info.value.args[0]


def test_validate_conf_none_valid(tmpdir):
    """ Test exception raises when [logme] section does not exist"""
    file = tmpdir.join('logme.ini')
    with file.open('w') as file_object:
        file_object.write('[foo]\nblah = 1')

    with pytest.raises(LogmeError) as e_info:
        validate_conf('blah', file)

    assert "is not a valid logme.ini file" in e_info.value.args[0]


def test_get_color_tpl():
    expected = {
        'colors': {
            'CRITICAL': {'color': 'PURPLE', 'style': 'BOLD'},
            'ERROR': 'RED',
            'WARNING': 'YELLOW',
            'INFO': 'None',
            'DEBUG': 'GREEN'
        }
    }
    color_tpl = get_color_tpl()

    assert color_tpl == expected


def test_get_tpl(tmpdir):
    log_path = tmpdir.join('log_dir')
    template = get_tpl('test_log', filename=log_path, level='INFO',
                       formatter='{name} : {message}')

    assert isinstance(template, dict)
    assert set(template['test_log'].keys()) == {'level', 'formatter', 'stream',
                                                'file', 'null'}
    assert template['test_log']['level'] == 'INFO'
    assert template['test_log']['file']['filename'] == log_path

    assert Path(log_path).parent.exists()


def test_map_template():
    sample_template = {
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

    input_options = {
        'level': 'DEBUG',
        'formatter': '{name} :: {message}'
    }

    map_template(sample_template, input_options)

    assert sample_template['level'] == sample_template['file']['level'] \
           == sample_template['stream']['level'] \
           == input_options['level']

    assert sample_template['formatter'] == input_options['formatter']
    assert sample_template['null']['level'] == 'NOTSET'


@pytest.mark.parametrize('level', [pytest.param('critical', id='lower case level option'),
                                   pytest.param('INFO', id='upper case level option'),
                                   pytest.param('eRRor', id='mixed case level option'),
                                   pytest.param('50', id='integer level option')])
def test_check_options_levels(level):
    assert check_options(level=level) is None


def test_check_option_filename(tmpdir):
    log_file = tmpdir.join('blah').join('filename.log')
    check_options(filename=log_file)

    assert Path(log_file).parent.exists()


def test_check_option_raise():
    with pytest.raises(LogmeError):
        check_options(level='blah')
