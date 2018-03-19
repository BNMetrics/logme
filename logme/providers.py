import inspect
from functools import update_wrapper, partial

from typing import Callable

import logging
from logging import handlers as logging_handlers

from .config import get_config_content
from .utils import ensure_dir, check_scope
from .exceptions import MisMatchScope, InvalidOption, InvalidConfig, DuplicatedHandler


class LogDecorator:
    """
        Behaves as a decorator to class/function/method.

            - Inject a keyword arg to function/method
            - Inject an attribute 'logger' to a class based decorator
    """

    def __init__(self, decorated: Callable, scope: str=None,
                 config: str=None, name: str=None):
        """
        Initialization of Logger decorator, all the optional arguments should be passed from logme.log()

        Required: scope
        Optional: config, name.
                (logger configuration will resolve to the default when not specified,
                *given logme.ini file exists in root dir*)

        """
        check_scope(scope, ['class', 'function'])

        self.decorated = decorated
        self.scope = scope

        # Get the module object of the decorated object
        module_obj = inspect.getmodule(self.decorated)

        logger_name = name if name else module_obj.__name__
        config_dict = get_config_content(module_obj.__file__, name=config)

        self.logger = LogmeLogger(logger_name, config_dict)

    def __get__(self, obj, _):
        """
        Descriptor for methods.

        - if self.decorated is a bound method of an object
        """
        return partial(self.__call__, obj)

    def __call__(self, *args, **kwargs):
        # Update the LogDecorator class to look like the decorated object
        update_wrapper(self, self.decorated)

        if self.scope == 'class' and inspect.isclass(self.decorated):
            self.decorated.logger = self.logger
            return self.decorated(*args, **kwargs)
        elif self.scope == 'function' and inspect.isfunction(self.decorated):
            return self.decorated(*args, **kwargs, logger=self.logger)

        raise MisMatchScope(f'{self.decorated.__name__} is not a {self.scope} scope')

    def __repr__(self):
        # Alter the string representation of LogDecorator class to look like the decorated object
        return repr(self.decorated)


class ModuleLogger:
    """
    Resolves to a LogmeLogger object based on the config and name passed from logme.log

    """
    def __init__(self, frame: int, config: str=None, name: str=None):
        """

        :param frame: frame number of the caller stack (1 if direct instantiate, 2 if instantiated from logme.log
        :param name: name of the logger
        :param config: configuration of the logger

        """
        module_frame = inspect.stack()[frame]
        module_obj = inspect.getmodule(module_frame.frame)

        logger_name = name if name else module_obj.__name__
        config_dict = get_config_content(module_frame.filename, name=config)

        self.logger = LogmeLogger(logger_name, config_dict)

    def __getattr__(self, attr):
        """
        Delegate the attributes and methods of self.logger to self
        """
        return getattr(self.logger, attr)


# ---------------------------------------------------------------------------
# Logger Object
# ---------------------------------------------------------------------------


class LogmeLogger:
    """
    Get a logger object with configured handlers

    """
    def __init__(self, name: str, config: dict):
        """
        :param name: name of the logger
        :param config: configuration of the logger
        """

        self.name = name
        self.config = config

        self._set_master_properties()

        self._set_handlers()

    def __getattr__(self, attr):
        """
        Delegate all the attributes and methods of logger to LogmeLogger Object
        """
        try:
            return getattr(self.logger, attr)
        except AttributeError:
            raise AttributeError(f"LogmeLogger object has no attribute '{attr}'.")

    @property
    def logger(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(self.master_level)

        return logger

    @property
    def handlers(self):
        # TODO: map handlers to a name:object dict
        return self.handlers

    def _set_master_properties(self):
        master_properties = {
            'master_formatter': logging.Formatter(self.config['formatter'], style='{'),
            'master_level': getattr(logging, self.config['level'].upper()),
            'handler_names':  [i for i in self.config.keys() if 'Handler' in i]

        }

        for k, v in master_properties.items():
            setattr(self, k, v)

    def _set_handlers(self):
        """
        Iterate through the config dict, set the active handlers
        """
        for handler_name in self.handler_names:

            if self.config[handler_name]['active'] is False:
                continue

            handler = self._get_handler(handler_name)

            level = self.config[handler_name].get('level')
            formatter = self.config[handler_name].get('formatter')
            self._config_handler(handler, formatter=formatter, level=level)

            if not self._handler_exist(handler):
                self.logger.addHandler(handler)

    def _get_handler(self, handler_name: str) -> logging.Handler:
        """ Get Handler object by name """

        try:
            handler_class = getattr(logging, handler_name)
        except AttributeError:
            handler_class = getattr(logging_handlers, handler_name)

        if handler_name == 'FileHandler':
            try:
                filename = self.config[handler_name]['filename']
                ensure_dir(filename)

                handler = handler_class(filename=filename)
            except TypeError:  # filename is None
                raise ValueError(f"file path for the {handler_name} must not be None")
        else:
            try:
                parse_args = {k: v for k, v in self.config[handler_name].items()
                              if k not in ['active', 'level', 'formatter']}

                handler = handler_class(**parse_args)
            except KeyError:
                raise InvalidConfig(f"{handler_name} is not configured in the logme.ini file, "
                                    f"current available handlers: {self.handler_names}")

        return handler

    def _config_handler(self, handler, level: str=None, formatter: str=None):
        """
        Configure the handler's level and formatter
        """
        # Set level
        if level:
            handler.setLevel(getattr(logging, level.upper()))
        else:
            handler.setLevel(self.master_level)

        # Set formatter
        if formatter:
            formatter_object = logging.Formatter(formatter, style='{')
            handler.setFormatter(formatter_object)
        else:
            handler.setFormatter(self.master_formatter)

    def _handler_exist(self, handler: logging.Handler) -> bool:
        """
        Check if logging handler already exists
        """
        for i in self.logger.handlers:
            handler_class = i.__class__
            handler_attr = self._get_handler_attr(handler)
            exist_attr = self._get_handler_attr(i)

            # Using type(handler) here because FileHandler inherit from StreamHandler,
            # and isinstance() will be True is checking a FileHandler object with StreamHandler class
            if type(handler) is handler_class and handler_attr == exist_attr:
                return True

        return False

    def add_handler(self, handler_type: str, formatter: str=None,
                    level: str=None, allow_duplicate: bool=False, **kwargs):
        """
        Add the handler to self.logger on adhoc basis

        :param handler_type: The type of handler, e.g. StreamHandler, SocketHandler
        :param formatter: formatter to be passed to the handler
        :param level: Level for the handler
        :param allow_duplicate: *USE WITH CAUTION*, this allows duplication of handlers in the same logger

        :param kwargs: arguments to be passed to the handler class

        """
        handler_class = getattr(logging, handler_type)

        handler = handler_class(**kwargs)
        self._config_handler(handler, level=level, formatter=formatter)

        if not self._handler_exist(handler) or allow_duplicate:
            self.logger.addHandler(handler)
        else:
            raise DuplicatedHandler(f"{handler_class} with the exact same configuration already exists, "
                                    f"add allow_duplicate=True to allow.")

    def _get_handler_attr(self, handler: logging.Handler) -> dict:
        """
        Get the *string* attribute of the handler
        """
        handler_attr = {'formatter': handler.formatter._fmt}

        for k, v in handler.__dict__.items():
            if isinstance(v, str) or str(v).isdigit():
                handler_attr[k] = v

        return handler_attr

    def reset_config(self, config_name: str=None, config: dict=None, name: str=None):
        """
        Used for alternative config. This is normally used for module scope loggers

        :param config_name: config names specified in the config
        :param config: config dict
        :param name: logger name to be changed to
        """
        # Check if the arguments are valid
        if config and config_name:
            raise InvalidOption("Can only set keyword argument of either 'config_name' or 'config', not both.")
        if not config and not config_name:
            raise InvalidOption("must specify one of 'config_name' or 'config'.")

        caller_file_path = inspect.getframeinfo(inspect.currentframe().f_back).filename
        if config_name:
            self.config = get_config_content(caller_file_path, config_name)
        else:
            self.config = config

        if name:
            self.name = name

        # Remove existing handlers and configure new
        for i in self.logger.handlers:
            self.logger.removeHandler(i)

        self._set_master_properties()
        self._set_handlers()
