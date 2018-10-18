import pytest

from pathlib import Path

from bnmutils import ConfigParser
from configparser import NoSectionError

from logme.exceptions import InvalidOption, InvalidLoggerConfig
from logme.utils import (get_logger_config, get_ini_file_path, get_config_content,
                         get_color_config, ensure_dir, check_scope)


@pytest.mark.parametrize('subpath, path_type, expected_path',
                         [pytest.param('test/my_test_dir', 'current', 'test/my_test_dir',
                                       id='make sure the exact dir exists'),
                          pytest.param('foo/my_dir/myfile.txt', 'parent', 'foo/my_dir',
                                       id='make sure the parent dir exists')])
def test_ensure_dir(tmpdir, subpath, path_type, expected_path):
    dir_path = Path(tmpdir) / Path(subpath)

    ensure_dir(dir_path, path_type=path_type)

    assert (Path(tmpdir) / Path(expected_path)).exists()


def test_ensure_dir_raise(tmpdir):
    with pytest.raises(InvalidOption):
        ensure_dir(tmpdir, path_type='cwd')


@pytest.mark.parametrize('scope, options', [pytest.param('function', ['function', 'class']),
                                            pytest.param('class', ['function', 'class', 'module', 'blah'])])
def test_check_scope_function(scope, options):
    assert check_scope(scope, options) is True


@pytest.mark.parametrize('conf_name, expected_master_level',
                         [
                             pytest.param(None, 'DEBUG', id='when no conf_name is being passed'),
                             pytest.param('my_test_logger', 'INFO', id='when conf_name is being passed')
                         ])
def test_get_logger_config(conf_name, expected_master_level):
    logger_config = get_logger_config(__file__, conf_name)

    assert logger_config['level'] == expected_master_level


@pytest.mark.parametrize('conf_name',
                         [
                             pytest.param('colors', id='colors passed as configuration'),
                             pytest.param('bunny', id='none existent config section')
                         ])
def test_get_logger_config_raise(conf_name):
    with pytest.raises(InvalidLoggerConfig):
        get_logger_config(__file__, conf_name)


def test_get_color_config():
    expected = {
        'CRITICAL': {'bg': 'red', 'color': 'white', 'style': 'Bold'},
        'ERROR': 'PURPLE',
        'WARNING': 'YELLOW',
        'INFO': 'GREEN',
        'DEBUG': 'WHITE'
    }
    color_conf = get_color_config(__file__)
    assert expected == color_conf


def test_color_config_with_none_value():
    """ Test for correct output when a value is None"""
    expected = {
        'CRITICAL': {'color': 'PURPLE', 'style': 'Bold'},
        'ERROR': 'RED',
        'WARNING': 'YELLOW',
        'INFO': None,
        'DEBUG': 'GREEN',
    }
    color_config = get_config_content(__file__, 'colors_test2')

    assert color_config == expected


def test_color_config_none_exist(tmpdir):
    """
    Ensure color config returns None if none existent
    """
    logme_file = tmpdir.join('logme.ini')

    logger_conifg = get_logger_config(__file__)
    config_dict = {'logme': logger_conifg}

    config = ConfigParser.from_dict(config_dict)

    with open(logme_file, 'w') as file:
        config.write(file)

    color_config = get_color_config(logme_file)

    assert color_config is None


def test_get_config_content():
    conf_content = get_config_content(__file__, 'my_test_logger')

    assert type(conf_content) == dict
    assert type(conf_content['FileHandler']) == dict
    assert conf_content['level'] == 'INFO'


def test_get_config_content_ver11():
    """
    Added for v1.1.0, ensure get_config_content() works with both v1.1.* and v1.0.*
    """
    expected = {'level': 'DEBUG',
                'formatter': '{asctime} - {name} - {levelname} - {message}',
                'stream': {
                    'type': 'StreamHandler',
                    'active': True,
                    'level': 'INFO'},
                'file': {
                    'type': 'FileHandler',
                    'active': False,
                    'level': 'DEBUG',
                    'filename': 'mylogpath/foo.log'},
                'null':
                    {
                        'type': 'NullHandler',
                        'active': False,
                        'level': 'DEBUG'}
                }
    conf_content = get_config_content(__file__, 'ver11_config')

    assert conf_content == expected


def test_get_config_content_ver13():

    conf_content = get_logger_config(__file__, 'ver13_config')
    print(conf_content)


def test_get_config_content_raise():
    with pytest.raises(NoSectionError):
        get_config_content(__file__, 'blah')


def test_get_ini_file_path():
    conf_path = get_ini_file_path(__file__)

    assert conf_path == Path(__file__).parent / 'logme.ini'


def test_get_ini_file_path_raise(tmpdir, monkeypatch):
    monkeypatch.setattr('pathlib.Path.root', tmpdir)

    target_dir = tmpdir.mkdir('test').mkdir('test_again')
    with pytest.raises(ValueError):
        get_ini_file_path(target_dir)


def test_get_ini_file_path_script_raise(tmpdir, monkeypatch):
    monkeypatch.setattr('pathlib.Path.root', tmpdir)
    target = Path(tmpdir) / 'script.py'
    open(target, 'a').close()

    with pytest.raises(ValueError):
        get_ini_file_path(target.name)
