import pytest

from pathlib import Path
from click.testing import CliRunner

from logme.config import read_config, get_ini_file_path
from logme.exceptions import InvalidConfig


class TestConfig:

    @classmethod
    def setup(cls):
        cls.runner = CliRunner()

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

    def test_get_ini_file_path(self):
        conf_path = get_ini_file_path(__file__)

        assert conf_path == Path(__file__).parent.parent / 'logme.ini'

