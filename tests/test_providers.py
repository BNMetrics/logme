import pytest

from logme.providers import LogDecorator, ModuleLogger


class TestProviders:
    def test_log_decorator_function(self):
        @LogDecorator
        def stub_funct(logger, blah):
            logger.info('hello!')
            return logger
