import sys
import inspect
import logging

from .config import get_config_content
from .exceptions import MisMatchScope


class LogDecorator:

    def __init__(self, decorated, scope=None, level=None, formatter=None, file=None):
        self.decorated = decorated
        self.scope = scope

        name = decorated.__name__

        decorated_file_path = inspect.getmodule(self.decorated).__file__
        config = get_config_content(decorated_file_path)

        self.logger = LogmeLogger(name, config, level=level, formatter=formatter, file=file)

    def __call__(self, *args, **kwargs):

        if self.scope == 'class' and inspect.isclass(self.decorated):
            self.decorated.logger = self.logger

            return self.decorated(*args, **kwargs)
        elif inspect.isfunction(self.decorated):

            return self.decorated(self.logger, *args, **kwargs)

        raise MisMatchScope(f'{self.decorated} is not a {self.scope} scope')


class ModuleLogger:
    def __init__(self, name=None):
        pass


# ---------------------------------------------------------------------------
# Logger Object
# ---------------------------------------------------------------------------

class LogmeLogger:
    """
    config = get_config()

    LogmeLogger(name, **config)

    """
    def __init__(self, name, config, **kwargs):

        self.name = name

        self.config = config

        self.caller_file_name = inspect.getmodule(inspect.currentframe().f_back).__name__

        for k, v in kwargs.items():
            if v is not None:
                self.config[k] = v

    def __getattr__(self, attr):
        return getattr(self.logger, attr)

    @property
    def logger(self):

        logger = logging.getLogger(self.caller_file_name)

        level = getattr(logging, self.config['level'].upper())
        logger.setLevel(level)

        logger = self._set_handlers(logger)

        return logger

    def _set_handlers(self, logger):

        formatter = logging.Formatter(self.config['formatter'], style='{')

        if self.config['StreamHandler'] is True:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)

            logger.addHandler(stream_handler)

        return logger

    def set_config(self, conf_name=None):
        """
        Used for alternative config.

        :param logger_name:
        :return:
        """
        caller_file_path = inspect.getframeinfo(inspect.currentframe().f_back).filename

        return caller_file_path

