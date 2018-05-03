import pytest
import logging

from click.testing import CliRunner

from logme.cli import cli
from logme.config import get_config_content
from logme.providers import LogmeLogger


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


@pytest.fixture
def logger_from_provider():
    config = get_config_content(__file__)
    logger = LogmeLogger('test_logger', config)

    yield logger

    for i in logger.logger.handlers:
        logger.removeHandler(i)


@pytest.fixture
def ver11_logger():
    ver11_conf = get_config_content(__file__, 'ver11_config')
    ver11_logger = LogmeLogger('test_ver11', ver11_conf)

    yield ver11_logger

    for i in ver11_logger.logger.handlers:
        ver11_logger.removeHandler(i)


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


