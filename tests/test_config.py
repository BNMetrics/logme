import pytest

from pathlib import Path

from logme.config import (get_logger_config, read_config, get_ini_file_path,
                          get_config_content, get_color_config)
from logme.utils import dict_to_config, flatten_config_dict, cd
from logme.exceptions import InvalidConfig


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
    with pytest.raises(InvalidConfig):
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

    config_dict = {'logme': flatten_config_dict(get_logger_config(__file__))}
    config = dict_to_config(config_dict)

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


def test_get_config_content_raise():
    with pytest.raises(InvalidConfig):
        get_config_content(__file__, 'blah')


def test_read_config(tmpdir_class_scope):
    project_dir, _ = tmpdir_class_scope

    config = read_config(Path(project_dir) / 'logme.ini')

    assert config.sections() == ['colors', 'logme']


def test_read_config_empty(tmpdir):
    file = tmpdir.join('foo.ini')
    file.open('w').close()

    assert Path(file).exists()

    with pytest.raises(InvalidConfig):
        read_config(file)


def test_read_config_file_non_exist():

    with pytest.raises(InvalidConfig):
        read_config('blah.ini')


def test_get_ini_file_path():
    conf_path = get_ini_file_path(__file__)

    assert conf_path == Path(__file__).parent / 'logme.ini'


def test_get_ini_file_path_raise(tmpdir, monkeypatch):
    monkeypatch.setattr('pathlib.Path.root', tmpdir)

    target_dir = tmpdir.mkdir('test').mkdir('test_again')
    with pytest.raises(ValueError):
        get_ini_file_path(target_dir)


