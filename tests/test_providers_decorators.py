import pytest

from logme.config import get_config_content
from logme.exceptions import MisMatchScope, LogmeError
from logme.providers import LogDecorator, ModuleLogger, LogmeLogger


def dummy_func(*args, **kwargs):
    logger = kwargs['logger']
    logger.info('my dummy function message.')

    return logger


class DummyClass:
    pass


@pytest.mark.parametrize('args, logger_name, config_name',
                         [pytest.param({'config': None, 'name': None}, __name__, 'logme',
                                       id='Default config name and logger name'),
                          pytest.param({'config': 'my_test_logger', 'name': 'dummy_logger2'},
                                       'dummy_logger2', 'my_test_logger',
                                       id='custom config name and logger name'),
                          ])
def test_log_decorator_function(caplog, args, logger_name, config_name):
    global dummy_func

    dummy = LogDecorator(dummy_func, scope='function', **args)

    logger = dummy('blah')

    assert logger.name == logger_name
    assert logger.config == get_config_content(__file__, name=config_name)
    assert caplog.record_tuples[0] == (logger_name, 20, 'my dummy function message.')


@pytest.mark.parametrize('input_scope, exception', [pytest.param('class', MisMatchScope, id='Mismatching scope raises'),
                                                    pytest.param('foo', LogmeError, id='bogus scope being passed')
                                                    ])
def test_log_decorator_function_raise(input_scope, exception):
    global dummy_func

    with pytest.raises(exception):
        dummy = LogDecorator(dummy_func, scope=input_scope)
        dummy()


def test_log_decorator_class():
    dummy_class = LogDecorator(DummyClass, scope='class')
    obj = dummy_class()

    assert hasattr(obj, 'logger')
    assert isinstance(obj.logger, LogmeLogger)


def test_log_decorator_class_raise():
    with pytest.raises(MisMatchScope):
        dummy_class = LogDecorator(DummyClass, scope='function')
        obj = dummy_class()


def test_module_logger(caplog):
    my_logger = ModuleLogger(frame=1, name='test_module_logger')

    assert type(my_logger.logger) == LogmeLogger
    assert my_logger.name == 'test_module_logger'
    assert my_logger.master_formatter._fmt == '{asctime} - {name} - {levelname} - {module}::{funcName}::{message}'
    assert my_logger.config == get_config_content(__file__)

    my_logger.info('my test module logger content')
    assert caplog.record_tuples[0] == ('test_module_logger', 20, 'my test module logger content')



