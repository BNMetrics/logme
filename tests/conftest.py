import pytest
import logging

from click.testing import CliRunner

from logme.cli import cli
from logme.config import get_config_content


@pytest.fixture(scope='class')
def tmpdir_class_scope(tmpdir_factory):

    project_dir = tmpdir_factory.mktemp('my_test_project')
    nested_dir = project_dir.mkdir('test_dir')

    runner = CliRunner()

    runner.invoke(cli, ['init', '-p', str(project_dir)])

    yield project_dir, nested_dir


@pytest.fixture
def file_config_content(tmpdir):
    config = get_config_content(__file__, 'filehandler_conf')
    config['FileHandler']['filename'] = tmpdir.join(config['FileHandler']['filename'])

    yield config


# ---------------------------------------------------------------------------
# handler fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def socket_handler():
    handler = logging.handlers.SocketHandler(host='127.0.0.7', port='8080')
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('{asctime} - {name}::{message}')
    handler.setFormatter(formatter)

    yield handler


