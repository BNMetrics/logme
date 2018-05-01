import pytest

from pathlib import Path
from click.testing import CliRunner

from logme.config import read_config, get_ini_file_path, get_config_content
from logme.exceptions import InvalidConfig


class TestConfig:

    @classmethod
    def setup(cls):
        cls.runner = CliRunner()

    @pytest.mark.parametrize('conf_name, expected_level',
                             [pytest.param(None, 'DEBUG', id='when no conf_name is being passed'),
                              pytest.param('my_test_logger', 'INFO', id='when conf_name is being passed')])
    def test_get_config_content(self, conf_name, expected_level):
        conf_content = get_config_content(__file__, conf_name)

        assert type(conf_content) == dict
        assert type(conf_content['FileHandler']) == dict
        assert conf_content['level'] == expected_level

    def test_get_config_content_raise(self):
        with pytest.raises(InvalidConfig):
            get_config_content(__file__, 'blah')

    def test_read_config(self, tmpdir_class_scope):
        project_dir, _ = tmpdir_class_scope

        config = read_config(Path(project_dir) / 'logme.ini')

        assert config.sections() == ['logme']

    def test_read_config_empty(self, tmpdir):
        file = tmpdir.join('foo.ini')
        file.open('w').close()

        assert Path(file).exists()

        with pytest.raises(InvalidConfig):
            read_config(file)

    def test_read_config_file_non_exist(self):

        with pytest.raises(InvalidConfig):
            read_config('blah.ini')

    def test_read_config_type_error(self):
        pass

    def test_get_ini_file_path(self):
        conf_path = get_ini_file_path(__file__)

        assert conf_path == Path(__file__).parent / 'logme.ini'

    def test_get_ini_file_path_raise(self, tmpdir, monkeypatch):
        monkeypatch.setattr('pathlib.Path.root', tmpdir)

        target_dir = tmpdir.mkdir('test').mkdir('test_again')
        with pytest.raises(ValueError):
            get_ini_file_path(target_dir)


