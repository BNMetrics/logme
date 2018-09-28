import inspect
import warnings

from functools import partial
from typing import Callable, Union

import logging
from logging import handlers as logging_handlers

from .color_provider import ColorFormatter
from .utils import ensure_dir, get_logger_config, get_color_config
from .exceptions import InvalidOption, DuplicatedHandler, LogmeError


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

        config_dict = get_logger_config(module_obj.__file__, name=config)
        color_config = get_color_config(module_obj.__file__)

        self.logger = LogmeLogger(logger_name, config_dict,
                                  color_config=color_config)


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

        config_dict = get_logger_config(module_frame.filename, name=config)
        color_config = get_color_config(module_frame.filename)

        self.logger = LogmeLogger(logger_name, config_dict,
                                  color_config=color_config)

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
    def __init__(self, name: str, config: dict, color_config: dict=None):
        """
        :param name: name of the logger
        :param config: configuration of the logger
        """

        self._name = name
        self.config = config
        self.color_config = color_config

        self.handlers = {}
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

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"

    @property
    def name(self):
        """
        To prevent name from being set outside of __init__,
        as the change of name will cause re-instantiation of logging.Logger object.
        """
        return self._name

    @property
    def logger(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(self.master_level)

        return logger

    @property
    def disabled(self):
        return self.logger.disabled

    @disabled.setter
    def disabled(self, val):
        self.logger.disabled = val

    @property
    def master_formatter(self):
        return self._master_formatter

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
            'handler_names':  [i for i in self.config.keys()
                               if i not in ['level', 'formatter']]

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
                handler_obj = self.handlers[handler_name]
                self._config_handler(handler_obj, level=level,
                                     formatter=formatter, set_from_master=True)
            else:
                handler_type = self._get_handler_type(handler_name)
                self.add_handler(handler_name, handler_type, level=level, formatter=formatter,
                                 skip_duplicate=True, **parse_args)

    def _get_handler_args(self, handler_name):
        """
        Get the args passed into handler from config
        """
        parse_args = {k: v for k, v in self.config[handler_name].items()
                      if k not in ['type', 'active', 'level', 'formatter']}

        return parse_args

    def _get_handler_type(self, handler_name) -> str:
        """
        Get the type of the handler from handler_name declared in the config.

        :return: e.g. StreamHandler, SocketHandler
        """
        try:
            handler_type = self.config[handler_name]['type']
        except KeyError:
            # Deprecation warning
            warnings.warn("Current configuration is deprecated, run 'logme upgrade' in your "
                          "project root to upgrade your logme.ini file",
                          category=DeprecationWarning)

            handler_type = handler_name

        return handler_type

    def _config_handler(self, handler: logging.Handler, level: Union[str, int]=None,
                        formatter: Union[str, dict]=None, set_from_master: bool=False):

        """
        Configure the handler's level and formatter

        :param handler: logging.Handler type object
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
        if type(handler) == logging.StreamHandler:
            formatter_class = partial(ColorFormatter,
                                      color_config=self.color_config)
        else:
            formatter_class = logging.Formatter

        if formatter:
            self._set_formatter(handler, formatter_class, formatter)
        elif set_from_master:
            self._set_formatter(handler, formatter_class, self.master_formatter)

    def _get_level(self, level: Union[str, int]) -> int:
        """
        Get the level number of the logger
        """
        if isinstance(level, str):
            try:
                return logging._nameToLevel[level.upper()]
            except KeyError:
                raise InvalidOption(f"'{level}' is not a valid level option")
        if isinstance(level, int):  # logging.ERROR is also type of int
            return level

    def _get_formatter_args(self, formatter: Union[str, dict]) -> dict:
        """
        Get argument to be passed to logging.Formatter
        """
        if isinstance(formatter, dict):
            return formatter
        elif isinstance(formatter, str):
            return {'fmt': formatter, 'style': '{'}

        raise ValueError(f"Invalid formatter type: '{type(formatter)}', "
                         f"formatter must be passed as either dict or string")

    def _set_formatter(self, handler: logging.Handler, formatter_class: type,
                       formatter: Union[str, dict]):
        """
        Set the formatter with the handler and formatter class specified
        """
        args = self._get_formatter_args(formatter)
        formatter_object = formatter_class(**args)

        handler.setFormatter(formatter_object)

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

    def add_handler(self, handler_name: str, handler_type: str, formatter: Union[str, dict]=None,
                    level: Union[str, int]=None, allow_duplicate: bool=False, skip_duplicate: bool=False, **kwargs):
        """
        Add the handler to self.logger on adhoc basis

        :param handler_name: The name of the handler:
                                    - Same as handler_type.
                                    - key for handlers in ini file. *version >= 1.1.0*
        :param handler_type: The type of handler, e.g. StreamHandler, SocketHandler
        :param formatter: formatter to be passed to the handler
        :param level: Level for the handler
        :param allow_duplicate: *USE WITH CAUTION*, this allows duplication of handlers in the same logger
        :param skip_duplicate: Skip the duplicated handler

        :param kwargs: arguments to be passed to the handler class

        """
        if self.handlers.get(handler_name):
            raise LogmeError(f"Handler with name {handler_name} already exists!")

        try:
            handler_class = getattr(logging, handler_type)
        except AttributeError:
            handler_class = getattr(logging_handlers, handler_type)

        # Ensure filename for handlers are passed in and directory is created
        self._ensure_filepath(handler_class, **kwargs)

        handler = handler_class(**kwargs)
        self._config_handler(handler, level=level,
                             formatter=formatter, set_from_master=True)

        if self._handler_exist(handler):
            if allow_duplicate:
                self.logger.addHandler(handler)
                self.handlers[handler_name] = handler
                return
            if skip_duplicate:
                return
            else:
                raise DuplicatedHandler(f"{handler_class} with the exact same configuration already exists, "
                                        f"add allow_duplicate=True to allow.")
        else:
            self.logger.addHandler(handler)
            self.handlers[handler_name] = handler

    def _ensure_filepath(self, handler_class, **kwargs):
        """
        Ensure the filename is being passed into the handler class,
        Make the directory if it doesn't exist

        :param handler_class: Handler class from logging module
        :param kwargs: arguments to be passed into the the class when instantiate an object
        """

        required_args = str(inspect.signature(handler_class))

        if 'filename,' in required_args:
            try:
                filename = kwargs['filename']
                ensure_dir(filename)
            except KeyError:  # filename is None or not Passed in
                raise ValueError(f"file path for the {handler_class} must not be None")

    def _get_handler_attr(self, handler: logging.Handler) -> dict:
        """
        Get the *string* attribute of the handler
        """
        handler_attr = {'formatter': handler.formatter._fmt}

        for k, v in handler.__dict__.items():
            if isinstance(v, str) or str(v).isdigit():
                handler_attr[k] = v

        return handler_attr

    def reset_config(self, config: str=None, config_dict: dict=None, name: str=None):
        """
        Used for alternative config. This is normally used for module scope loggers

        :param config: config name specified in the config
        :param config_dict: config dict
        :param name: logger name to be changed to
        """
        # Check if the arguments are valid
        if config and config_dict:
            raise InvalidOption("Can only set keyword argument of either 'config_name' or 'config', not both.")
        if not config and not config_dict:
            raise InvalidOption("must specify one of 'config_dict' or 'config'.")

        caller_file_path = inspect.getframeinfo(inspect.currentframe().f_back).filename
        if config:
            self.config = get_logger_config(caller_file_path, config)
        else:
            self.config = config_dict

        # Remove existing logger from Logger manager dict
        del logging.Logger.manager.loggerDict[self.name]

        if name:
            self._name = name

        self.handlers = {}
        self._set_master_properties()
        self._set_handlers_from_conf()

    def reconfig_handler(self, handler_name: str, level: Union[str, int]=None, formatter: Union[str, dict]=None):
        """
        Reconfigure an existing handler's level and formatter.
        *This can be used to configure a handler for a specific logger to be different from the config in Logme.ini*

        :param handler_name: **case sensitive**. name of the handler, specified as a option key in ini file
        :param level: the new level to be set
        :param formatter: the new formatter to be set. '{' style

        """
        if not level and not formatter:
            raise InvalidOption("Set at least one of 'level' or 'formatter' for reconfiguration.")

        try:
            handler_obj = self.handlers[handler_name]
            self._config_handler(handler_obj, level=level,
                                 formatter=formatter)
        except KeyError:
            raise LogmeError(f"{handler_name} is not found in this logger, either use add_handle() to add this handler")
