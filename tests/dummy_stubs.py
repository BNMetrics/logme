import logme

"""Decorator use cases"""


# ---------------------------------------------------------------------------
# Dummy decorated *function*
# ---------------------------------------------------------------------------
@logme.log
def dummy_function_default(name, logger=None, **kwargs):
    """Also tests the case of when more kwargs are needed to be passed"""
    logger.debug('test function logger.')
    return logger, name, kwargs


@logme.log(config='my_test_logger', name='custom_test_logger')
def dummy_function_custom(name, logger=None):
    logger.info('test function logger with custom params')

    return logger, name


# ---------------------------------------------------------------------------
# Dummy decorated *class*
# ---------------------------------------------------------------------------
@logme.log
class DummyClassDefault:
    def __init__(self, arg):
        self.arg = arg


@logme.log(config='my_test_logger', name='custom_class_logger')
class DummyClassCustom:
    def __init__(self, arg):
        self.arg = arg


@logme.log
class DummyClassForExtension:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2

    def log_this(self):
        self.logger.info('my logging message')


class DummyClassWithMethods:
    @logme.log(name='class_with_methods')
    def method_one(self, logger=None):
        logger.debug('test class with method logging message.')
        pass

    @logme.log(name='another_logger_with_args', config='my_test_logger')
    def method_with_args(self, name, age, logger=None, **kwargs):
        logger.warning('method logger with args')
        return name, age, kwargs


# ---------------------------------------------------------------------------
# Dummy module logger
# ---------------------------------------------------------------------------
module_logger = logme.log(scope='module', name='change_config')


def log_this():
    module_logger.info('change my config.')
    return module_logger


# null module handler test
null_module_logger = logme.log(scope='module', config='null_config', name='null_module')


def my_log_null():
    null_module_logger.critical('expect output after config_change')


# ---------------------------------------------------------------------------
# Others: Config change
# ---------------------------------------------------------------------------
@logme.log(config='change_master_conf', name='change_master_level')
def dummy_func_change_master_level(logger=None):
    # Changing the master level with non specified level on handlers
    logger.master_level = 'ERROR'
    logger.info('blah')

    return logger


@logme.log(config='change_master_conf', name='change_master_format')
def dummy_func_change_master_format(logger=None):
    logger.master_formatter = '{funcName}::{message}'

    logger.info('Changed master_formatter')

    return logger


@logme.log(config='logger_with_handler_conf', name='master_unaffected')
def dummy_func_change_master_format_with_handler_unaffected(logger=None):
    logger.master_formatter = '{funcName} - {message}'

    logger.info('changed master_formatter, handler formatter should not change')

    return logger


@logme.log(name='handler_level_change')
def dummy_func_change_handler_level(logger=None):
    logger.reconfig_handler('StreamHandler', level='WARNING')

    return logger


@logme.log(name='ve11_handler_formatter_reconfig', config='ver11_config')
def ver11_handler_formatter_reconf(my_arg, logger=None):
    logger.reconfig_handler('stream', formatter='{funcName} - {levelname} :: {message}')
    logger.error(my_arg)

    return logger


@logme.log(name='config_change_logger')
class DummyClassChangeConfig:
    def __init__(self):
        pass

    def change_my_level(self):
        self.logger.reconfig_handler('StreamHandler', level=50)

