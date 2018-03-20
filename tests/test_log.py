import pytest
from pathlib import Path

from .dummy_stubs import *

import logme
from logme import _get_logger_decorator
from logme.providers import LogmeLogger, ModuleLogger
from logme.exceptions import LogmeError


# ---------------------------------------------------------------------------
# Test logme decorator and module logger
# ---------------------------------------------------------------------------
def test_function_logger_default(caplog):
    logger, _, age = dummy_function_default('blah', age=6)

    assert caplog.record_tuples[0] == (dummy_function_default.__module__, 10, 'test function logger.')

    assert dummy_function_default.__doc__ == "Also tests the case of when more kwargs are needed to be passed"
    assert logger.name == dummy_function_default.__module__
    assert type(logger) == LogmeLogger
    assert logger.master_level == 10

    assert age == {'age': 6}


def test_function_logger_custom(caplog):
    logger, _ = dummy_function_custom('foo')

    assert caplog.record_tuples[0] == ('custom_test_logger', 20, 'test function logger with custom params')


def test_function_wrong_scope():
    with pytest.raises(LogmeError):
        @logme.log(scope='Blah')
        def dummy_function_wrong_scope():
            pass


def test_class_logger_default():
    obj = DummyClassDefault()

    assert hasattr(obj, 'logger')
    assert obj.logger.name == obj.__module__


@pytest.mark.parametrize('scope', [pytest.param('Module', id='capital first letter'),
                                   pytest.param('module', id='Happy path, all lower case'),
                                   pytest.param('modUlE', id='random capital letter')
                                   ])
def test_module_logger(caplog, scope):
    logger = logme.log(scope=scope, config='my_test_logger', name='blah')

    assert type(logger) == ModuleLogger
    assert logger.name == 'blah'

    logger.info('module logger message.')

    assert caplog.record_tuples[0] == ('blah', 20, 'module logger message.')


def test_class_with_method(caplog):
    obj = DummyClassWithMethods()

    obj.method_one()

    assert caplog.record_tuples[0] == ('class_with_methods', 10, 'test class with method logging message.')


def test_method_with_args(caplog):
    obj = DummyClassWithMethods()

    name, age, other = obj.method_with_args('Luna', '1', foo='hello', bar='bye')

    assert name == 'Luna'
    assert age == '1'
    assert other == {'foo': 'hello', 'bar': 'bye'}

    assert caplog.record_tuples[0] == ('another_logger_with_args', 20, 'method logger with args')


def test_change_logging_config(file_config_content):
    module_logger.reset_config(config=file_config_content)

    log_path = Path(file_config_content['FileHandler']['filename'])
    assert log_path.exists()

    log_this()
    with open(log_path) as file:
        assert file.readline() == "change_config::change my config.\n"


# ---------------------------------------------------------------------------
# Tests for others, _get_logger_decorator()
# ---------------------------------------------------------------------------
def test_get_logger_decorator_raise():
    with pytest.raises(LogmeError) as e_info:
        _get_logger_decorator('hello')

