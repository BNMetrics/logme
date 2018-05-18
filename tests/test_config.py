import pytest

from pathlib import Path

from logme.config import get_logger_config, read_config, get_ini_file_path, get_config_content
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
    with pytest.raises(InvalidConfig) as e_info:
        get_logger_config(__file__, conf_name)


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


def test_get_config_content_color():
    colors = get_config_content(__file__, 'colors')
    print(colors)

def test_get_config_content_raise():
    with pytest.raises(InvalidConfig):
        get_config_content(__file__, 'blah')


def test_read_config(tmpdir_class_scope):
    project_dir, _ = tmpdir_class_scope

    config = read_config(Path(project_dir) / 'logme.ini')

    assert config.sections() == ['logme']


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


