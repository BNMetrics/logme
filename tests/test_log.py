import pytest
import logging
from pathlib import Path

from .dummy_stubs import *

import logme
from logme import _get_logger_decorator
from logme.providers import LogmeLogger, ModuleLogger
from logme.exceptions import LogmeError, MisMatchScope


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
    obj = DummyClassDefault('foo')

    assert hasattr(obj, 'logger')
    assert obj.logger.name == obj.__module__
    assert obj.arg == 'foo'


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


def test_mismatch_scope_function():
    with pytest.raises(MisMatchScope):
        @logme.log(scope='class')
        def dummy_func_mismatch_scope(logger=None):
            logger.info('blah')

            return logger


def test_mismatch_scope_class():
    with pytest.raises(MisMatchScope):
        @logme.log(scope='function')
        class WrongClass: pass


def test_module_logger_null_handler():
    null_module_logger.add_handler('stream', 'StreamHandler', formatter='{name}-{message}', level='debug')

    my_log_null()


# ---------------------------------------------------------------------------
# Tests for config change, master_level/master_formatter
# ---------------------------------------------------------------------------
def test_change_logging_config(file_config_content):
    assert module_logger.logger.name == 'change_config'

    module_logger.reset_config(config_dict=file_config_content, name='changed_name')

    log_path = Path(file_config_content['FileHandler']['filename'])
    assert log_path.exists()

    log_this()
    with open(log_path) as file:
        assert file.readline() == "changed_name::change my config.\n"

    assert module_logger.logger.name == module_logger.name == 'changed_name'

    # Ensure old logger does not exist
    assert not logging.Logger.manager.loggerDict.get('change_config')

    old_logger = logging.getLogger('change_config')
    assert len(old_logger.handlers) == 0
    assert old_logger.level == 0


def test_change_logging_master_level():
    logger = dummy_func_change_master_level()

    assert logger.level == 40
    assert logger.handlers['StreamHandler'].level == 40


def test_change_logging_master_formatter():
    logger = dummy_func_change_master_format()

    assert logger.master_formatter._fmt == '{funcName}::{message}'
    assert logger.handlers['StreamHandler'].formatter._fmt == '{funcName}::{message}'


def test_change_master_formatter_handler_unaffected():
    logger = dummy_func_change_master_format_with_handler_unaffected()

    handler = logger.handlers['StreamHandler']
    assert logger.master_formatter._fmt == '{funcName} - {message}'
    assert handler.formatter._fmt == '{name} :: {funcName} :: {levelname} :: {message}'


def test_class_logger_handler_level_change():
    obj = DummyClassChangeConfig()
    obj.change_my_level()
    
    assert obj.logger.handlers['StreamHandler'].level == 50


def test_function_handler_level_change():
    logger = dummy_func_change_handler_level()

    handler = logger.handlers['StreamHandler']
    assert handler.level == 30
    assert logger.level == logger.master_level == 10


def test_v11_handler_formatter_reconf():
    logger = ver11_handler_formatter_reconf('hello')

    handler = logger.handlers['stream']
    assert handler.level == 20
    assert handler.formatter._fmt == '{funcName} - {levelname} :: {message}'


# ---------------------------------------------------------------------------
# Tests for others, _get_logger_decorator()
# ---------------------------------------------------------------------------
def test_get_logger_decorator_raise():
    with pytest.raises(LogmeError) as e_info:
        _get_logger_decorator('hello')
