import inspect

from typing import Callable, Union

import logging
from logging import handlers as logging_handlers

from .config import get_config_content
from .utils import ensure_dir
from .exceptions import InvalidOption, InvalidConfig, DuplicatedHandler, LogmeError


class LogProvider:
    """
    Get a LogmeLogger object for decorated classes and functions/methods

    *LogmeLogger object is provided as a object property of this LogProvider*
    """

    def __init__(self, decorated: Callable, config: str=None, name: str=None):
        """
        Initialization of Logger Provider, all the optional arguments should be passed from logme.log()

        Required: scope
        Optional: config, name.
                (logger configuration will resolve to the default when not specified,
                *given logme.ini file exists in root dir*)

        """

        self.decorated = decorated

        # Get the module object of the decorated object
        module_obj = inspect.getmodule(self.decorated)

        logger_name = name if name else module_obj.__name__

        config_dict = get_config_content(module_obj.__file__, name=config)

        self.logger = LogmeLogger(logger_name, config_dict)


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
        self._set_handlers_from_conf()

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
    def master_formatter(self):
        return logging.Formatter(self._master_formatter, style='{')

    @master_formatter.setter
    def master_formatter(self, formatter):
        self._master_formatter = formatter
        self._set_handlers_from_conf(reconfig=True)

    @property
    def master_level(self):
        return self._get_level(self._master_level)

    @master_level.setter
    def master_level(self, level):
        self._master_level = level
        self._set_handlers_from_conf(reconfig=True)

    def _set_master_properties(self):
        master_properties = {
            '_master_formatter': self.config['formatter'],
            '_master_level': self.config['level'],
            'handler_names':  [i for i in self.config.keys() if 'Handler' in i]

        }

        for k, v in master_properties.items():
            setattr(self, k, v)

    def _set_handlers_from_conf(self, reconfig=False):
        """
        Iterate through the config dict, set the active handlers
        """
        for handler_name in self.handler_names:

            if self.config[handler_name]['active'] is False:
                continue

            level = self.config[handler_name].get('level')
            formatter = self.config[handler_name].get('formatter')

            parse_args = self._get_handler_args(handler_name)

            if reconfig:  # If true, reconfigure the existing handlers
                handler_obj = self.get_handler_by_name(handler_name)
                self._config_handler(handler_obj, level=level,
                                     formatter=formatter, set_from_master=True)
            else:
                self.add_handler(handler_name, level=level, formatter=formatter,
                                 skip_duplicate=True, **parse_args)

    def _get_handler_args(self, handler_name):
        """
        Get the args passed into handler from config
        """
        if handler_name == 'FileHandler':
            try:
                filename = self.config[handler_name]['filename']
                ensure_dir(filename)

            except (TypeError, KeyError):  # filename is None or not Passed in
                raise ValueError(f"file path for the {handler_name} must not be None")

        parse_args = {k: v for k, v in self.config[handler_name].items()
                      if k not in ['active', 'level', 'formatter']}

        return parse_args

    def _config_handler(self, handler, level: Union[str, int]=None,
                        formatter: str=None, set_from_master: bool=False):

        """
        Configure the handler's level and formatter

        :param handler: logger.Handler type object
        :param level: the level of the handler
        :param formatter: the formatter of the handler

        :param set_from_master: Set *level* or *formatter* from obj.master_level and obj.master_formatter

        """
        # Set level
        if level:
            log_level = self._get_level(level)
            handler.setLevel(log_level)
        elif set_from_master:
            handler.setLevel(self.master_level)

        # Set formatter
        if formatter:
            formatter_object = logging.Formatter(formatter, style='{')
            handler.setFormatter(formatter_object)
        elif set_from_master:
            handler.setFormatter(self.master_formatter)

    def _get_level(self, level: Union[str, int]):
        """
        Get the level number of the logger
        """
        if isinstance(level, str):
            return logging.getLevelName(level.upper())
        if isinstance(level, int):  # logging.ERROR is also type of int
            return level

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

    def add_handler(self, handler_type: str, formatter: str=None, level: Union[str, int]=None,
                    allow_duplicate: bool=False, skip_duplicate: bool=False, **kwargs):
        """
        Add the handler to self.logger on adhoc basis

        :param handler_type: The type of handler, e.g. StreamHandler, SocketHandler
        :param formatter: formatter to be passed to the handler
        :param level: Level for the handler
        :param allow_duplicate: *USE WITH CAUTION*, this allows duplication of handlers in the same logger
        :param skip_duplicate: Skip the duplicated handler

        :param kwargs: arguments to be passed to the handler class

        """
        try:
            handler_class = getattr(logging, handler_type)
        except AttributeError:
            handler_class = getattr(logging_handlers, handler_type)

        handler = handler_class(**kwargs)
        self._config_handler(handler, level=level,
                             formatter=formatter, set_from_master=True)

        if self._handler_exist(handler):
            if allow_duplicate:
                self.logger.addHandler(handler)
                return
            if skip_duplicate:
                return
            else:
                raise DuplicatedHandler(f"{handler_class} with the exact same configuration already exists, "
                                            f"add allow_duplicate=True to allow.")
        else:
            self.logger.addHandler(handler)

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
        self._set_handlers_from_conf()

    def reconfig_handler(self, handler_name: str, level: Union[str, int]=None, formatter: str=None):
        """
        Reconfigure an existing handler's level and formatter.
        *This can be used to configure a handler for a specific logger to be different from the config in Logme.ini*

        :param handler_name: **case sensitive**. name of the handler, e.g: StreamHandler, FileHandler
        :param level: the new level to be set
        :param formatter: the new formatter to be set. '{' format

        """
        if not level and not formatter:
            raise InvalidOption("Set at least one of 'level' or 'formatter' for reconfiguration.")

        handler_obj = self.get_handler_by_name(handler_name)

        if not handler_obj:
            raise LogmeError(f"{handler_name} is not found in this logger, either use add_handle() to add this handler")

        self._config_handler(handler_obj, level=level,
                             formatter=formatter)

    def get_handler_by_name(self, handler_name: str):
        """
        Get the handler of self.logger by name
        *return None if none existent*

        :param handler_name: **case sensitive**. name of the handler, e.g: StreamHandler, FileHandler

        """
        for i in self.logger.handlers:
            if i.__class__.__name__ == handler_name:
                return i

