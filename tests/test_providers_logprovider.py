import pytest

from logme.config import get_logger_config
from logme.providers import LogProvider, ModuleLogger, LogmeLogger


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
def test_log_decorator_function(args, logger_name, config_name):
    global dummy_func

    provider = LogProvider(dummy_func, **args)

    logger = provider.logger

    assert logger.name == logger_name
    assert logger.config == get_logger_config(__file__, name=config_name)


def test_module_logger(caplog):
    my_logger = ModuleLogger(frame=1, name='test_module_logger')

    assert type(my_logger.logger) == LogmeLogger
    assert my_logger.name == 'test_module_logger'
    assert my_logger.master_formatter == '{asctime} - {name} - {levelname} - {module}::{funcName}::{message}'
    assert my_logger.config == get_logger_config(__file__)

    my_logger.info('my test module logger content')
    assert caplog.record_tuples[0] == ('test_module_logger', 20, 'my test module logger content')



