=========
CHANGELOG
=========

1.3.2 (2018-10-21)
==================

**Bug Fixes**

- Fixed the issue with missing 'logme.ini' file caused `RecursionError: maximum recursion`: `issue ticket <https://github.com/BNMetrics/logme/issues/8>`_.



1.3.1 (2018-10-01)
==================

**Bug Fixes**

- Changed the `python_requires` from `>=3` to `>=3.6`, as many places supports f-string format notation.
- Fixed a typo in readthedocs Advanced, `logme.reset_configuration` should be `logme.reset_config`



1.3.0 (2018-09-28)
==================

**Improvement**

- Allowing configuration of `datefmt`, and `style` for master level `formatters` in logme.ini.
    - This change does not break the previous version, you can still specify only the `fmt`
    - Does not apply to `logme init` or `logme add {config_name}` command for generate automatic
    - Default `style` will still be `{` if none specified
- example:

.. code-block:: ini

    [my_config]
    level = DEBUG
    formatter =
        fmt: {asctime} - {name} - {levelname} - {message}
        datefmt: %Y/%m/%d
        style: {
    stream =
        type: StreamHandler
        active: True
        level: DEBUG
    file =
        type: FileHandler
        active: True
        level: DEBUG
        formatter: {name} :: {funcName} :: {levelname} :: {message}
        filename: mylogpath/foo.log



1.2.1 (2018-06-01)
==================

**Bug Fixes**

- Error handling for color_provider.py was outputting invalid error message when invalid style was passed in.


**Misc**

- Removed config.py, and moved everything configuration file related to `bnmutils <https://github.com/BNMetrics/bnmetrics-utils>`_ repository.
  Moved everything logme configuration related to utils.py
- Changed exception.py::InvalidConfig to InvalidLoggerConfig




1.2.0 (2018-05-23)
==================

**Bug Fixes**

- Made the ``name`` property in LogmeLogger object unsettable, as overriding/reassignment of this property will create a new
  logging.Logger object, and this results in lose of configured all handlers.


**Improvement**

- Allowing color output in the terminal for ``StreamHandlers``!
- Running ``logme upgrade`` will now automatically apply ``colors`` configuration in your ``logme.ini``


**Misc**

- Improved testing in ``test_log.py``

- ``config.py``
    * Added ``get_logger_config()`` to allow getting only configurations of loggers in ``logme.ini``.
      This enables ``get_config_content()`` to get color configurations
    * Added ``get_color_config()``to get color configurations

- ``LogmeLogger.reset_config()``
    * Removing the previous configured logger by deleting the logger from ``logging.Logger.manager.loggerDict``,
      instead of removing handlers on the existing loggers.
    * Added ``disabled`` property for disabling logger.



1.1.0 (2018-05-05)
==================

**Improvements**

- allowing multiple of the same type of handlers to be added, and retrieved by name
- added version to the cli, to check version, do ``logme -v``
- added ``upgrade`` command to upgrade ``logme.ini`` file to current version




1.0.7 (2018-05-01)
==================

**Bug Fixes**

- Minor change in ``config.py::read_config()``, ensure ConfigParser.read() accepts string format filepath. As os.Pathlike is not
  available in older version of python3, e.g 3.6.0



1.0.6 (2018-04-30)
==================

**Improvements**

- Improvements on docs, included documentation for ``Adhoc Config Change`` and ``Using Logme in installable packages``
- Int value can now be passed as logger/handler level configuration
- ``master_level`` and ``master_formatter`` attribute can be reconfigured by reassigning values, int/str value for ``master_level``,
  and str value for ``master_formatter``
- Handlers can now be reconfigured after logger creation by calling ``reconfig_handler`` method on specific handler


**Bug Fixes**

- Fixed f string typo in ``__init__.py::_get_logger_decorator()``
- Fixed a bug in ``utils.py::conf_item_to_dict()``, to split only on the first ': '

**Misc**

- Code clean up on providers.py



1.0.5 (2018-04-24)
==================

**Improvements**

- Simplified the logme.log decorator
- If decorated class is extended, ``obj.logger`` attribute is carried from the decorated parent class to extended classes

- Core functionality stays the same


**Bug Fixes**

- Fixed the issue with decorated class being none extendable.
- ``type()`` on decorated objects now returns correct types


**Misc**

- Changed ``LogDecorator`` class to ``LogProvider`` as it is no longer a decorator
- ``logme.log`` decorator used by function / class is now resolved from ``_get_logger_decorator()``
- Added test cases for decorated class extension.



1.0.4 (2018-04-18)
==================

- Minor changes on ``strip_blank_recursive()`` to catch ``SyntaxError`` when passing logger format.
- Made test cases for changing ``master_level`` on logger after instantiation
