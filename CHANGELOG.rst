=========
CHANGELOG
=========

1.0.4 (2018-04-18)
==================

- Minor changes on ``strip_blank_recursive()`` to catch ``SyntaxError`` when passing logger format.
- Made test cases for changing ``master_level`` on logger after instantiation


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
