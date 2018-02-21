import logme

"""Decorator use cases"""


@logme.log
def dummy_function_default(name, logger=None, **kwargs):
    """Also tests the case of when more kwargs are needed to be passed"""
    logger.debug('test function logger.')
    return logger, name, kwargs


@logme.log(config='my_test_logger', name='custom_test_logger')
def dummy_function_custom(name, logger=None):
    logger.info('test function logger with custom params')

    return logger, name


@logme.log
class DummyClassDefault:
    pass


@logme.log(config='my_test_logger', name='custom_class_logger')
class DummyClassCustom:
    pass


class DummyClassWithMethods:
    @logme.log(name='class_with_methods')
    def method_one(self, logger=None):
        logger.debug('test class with method logging message.')
        pass

    @logme.log(name='another_logger_with_args', config='my_test_logger')
    def method_with_args(self, name, age, logger=None, **kwargs):
        logger.info('method logger with args')
        return name, age, kwargs


module_logger = logme.log(scope='module', name='change_config')


def log_this():
    module_logger.info('change my config.')
    return module_logger
