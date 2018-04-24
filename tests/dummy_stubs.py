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
        logger.info('method logger with args')
        return name, age, kwargs


# ---------------------------------------------------------------------------
# Dummy module logger
# ---------------------------------------------------------------------------
module_logger = logme.log(scope='module', name='change_config')


def log_this():
    module_logger.info('change my config.')
    return module_logger


# ---------------------------------------------------------------------------
# Others
# ---------------------------------------------------------------------------
@logme.log
def dummy_func_change_level(logger=None):
    import logging
    logger.master_level = logging.ERROR
    logger.info('blah')

    return logger


