import inspect

from .cli import cli

from .exceptions import LogmeError
from .providers import LogDecorator, ModuleLogger


# TODO: pytest.fixture for reference on design
def log(scope='function', name=None):
    """

    returns a decorator or logger object

    """

    if callable(scope) and not inspect.isclass(scope):
        return LogDecorator(scope, scope='function')
    elif scope == 'module':
        return ModuleLogger(name=name)
    else:
        def wrapper(decorated):
            if scope in ['class', 'function']:
                return LogDecorator(decorated, name=name)

            raise LogmeError(f"scope {scope} is not supported, please use either "
                             f"'class' or 'module', default is 'function'")
        return wrapper


# def check_scope(scope: str) -> bool:
#     """
#
#     :param scope:
#     :raises: LogmeError
#
#     :return: True if scope is one of ['class', 'function']
#     """
#     if scope in ['class', 'function']:
#         return True
#     else:
#         raise LogmeError(f"scope {scope} is not supported, please use either "
#                          f"'class' or 'module', default is 'function'")
