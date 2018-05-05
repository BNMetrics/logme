=========
CHANGELOG
=========



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