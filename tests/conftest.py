import pytest
from click.testing import CliRunner

from logme.cli import cli


@pytest.fixture(scope='class')
def tmpdir_class_scope(tmpdir_factory):

    project_dir = tmpdir_factory.mktemp('my_test_project')
    nested_dir = project_dir.mkdir('test_dir')

    runner = CliRunner()

    runner.invoke(cli, ['init', '-p', str(project_dir)])

    yield project_dir, nested_dir