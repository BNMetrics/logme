"""




"""

import inspect

from .cli import cli

from .utils import check_scope
from .exceptions import LogmeError
from .providers import LogDecorator, ModuleLogger


def log(scope: str=None, config: str=None, name: str=None):
    """
    Returns a decorator or logger object

    :param scope: scope of the logger
    :param config: name of the logging config specified in logme.ini
    :param name: name of the logger

    """

    if isinstance(scope, str) and scope.lower() == 'module':
        return ModuleLogger(frame=2, config=config, name=name)

    if callable(scope):
        return _get_logger_decorator(scope, config=config, name=name)
    else:
        if scope:
            check_scope(scope.lower(), ['class', 'function', 'module'])

        def wrapper(decorated):
            return _get_logger_decorator(decorated, config=config, name=name)
        return wrapper


def _get_logger_decorator(callable_: callable, config: str=None, name: str=None) -> LogDecorator:
    """
    Get the loggerDecorator based on what kind of callable is being passed, class | function

    """
    if inspect.isclass(callable_):
        return LogDecorator(callable_, scope='class',
                            config=config, name=name)

    if inspect.isfunction(callable_):
        return LogDecorator(callable_, scope='function',
                            config=config, name=name)

    raise LogmeError("'{callable_}' must be a 'class' or a 'function'.")


__version__ = '1.0.3'
