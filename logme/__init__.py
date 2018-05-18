"""




"""

import inspect
from typing import Callable

from functools import wraps

from .cli import cli

from .utils import check_scope
from .exceptions import LogmeError, MisMatchScope
from .providers import LogProvider, ModuleLogger
from .__version__ import __version__


def log(scope: str=None, config: str=None, name: str=None):
    """
    Returns a decorator or logger object based on the *scope*.

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
            check_scope(scope.lower(), ['class', 'function'])

        def wrapper(decorated):
            return _get_logger_decorator(decorated, config=config, name=name, scope=scope)
        return wrapper


def _get_logger_decorator(callable_: callable, config: str=None, name: str=None, scope: str=None) -> Callable:
    """
    Get the logger decorator based on what kind of callable is being passed, class | function
            - Inject a keyword arg to function/method
            - Inject an attribute 'logger' to a class based decorator

    """
    if inspect.isclass(callable_):
        if scope and scope != 'class':
            raise MisMatchScope(f"{callable_} is a class, cannot be assigned to a '{scope}' scope")

        provider = LogProvider(callable_, config=config, name=name)
        callable_.logger = provider.logger
        return callable_

    if inspect.isfunction(callable_):
        if scope and scope != 'function':
            raise MisMatchScope(f"{callable_} is a class, cannot be assigned to a '{scope}' scope")

        provider = LogProvider(callable_, config=config, name=name)

        @wraps(callable_)
        def wrapper(*args, **kwargs):
            return callable_(*args, **kwargs, logger=provider.logger)

        return wrapper

    raise LogmeError(f"'{callable_}' must be a 'class' or a 'function'.")
