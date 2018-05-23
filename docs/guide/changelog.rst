.. _changelog:

Changelog
=========

v1.1.0 Updates
--------------
_____________________________________________________________________


**logme** is now capable of having the same type of handlers with different configuration in ``logme.ini``


old style:
~~~~~~~~~~

.. code-block:: ini

    level = DEBUG
    formatter = {asctime} - {name} - {levelname} - {module}::{funcName}::{message}
    StreamHandler =
        active: True
        level: DEBUG
    FileHandler =
        active: False
        level: DEBUG
        filename: mylogpath/foo.log
    NullHandler =
        active: False
        level: NOTSET

New Style:
~~~~~~~~~~

.. code-block:: ini

    [logme]
    level = DEBUG
    formatter = {asctime} - {name} - {levelname} - {message}
    stream =
        type: StreamHandler
        active: True
        level: INFO
    file =
        type: FileHandler
        active: False
        level: DEBUG
        filename: mylogpath/foo.log
    null =
        type: NullHandler
        active: False
        level: DEBUG
