.. _quickstart:

.. role:: red

Quickstart
==========


Installation
------------
_____________________________________________________________________

To install the latest version of logme via **pip**:

.. code-block:: bash

    $ pip3 install logme


Configurations
--------------
_____________________________________________________________________

Initialization
~~~~~~~~~~~~~~

To use logme for your project, you will need to cd into your project root:

.. code-block:: bash

    $ cd /path/to/project_root

    $ logme init

Then you will see a configuration file 'logme.ini' created, it looks like this:

.. code-block:: ini

    [logme]
    level = DEBUG
    formatter = {asctime} - {name} - {levelname} - {message}
    StreamHandler =
        active: True
        level: DEBUG
    FileHandler =
        active: True
        level: DEBUG
        filename: None
    NullHandler =
        active: False
        level: NOTSET

This is the file where you add configurations for your logging. each block of configuration is independent,
and you can apply the same configuration blog to different loggers. You can have as many of them as you like.

.. note:: Toplevel **level** and **formatter** are master level handler configurations.
   This means if the level or/and formatter on each handler are not specified,
   the handlers will use the master level ones. With that said, *level* and *formatter* can be configured
   on handler level by adding these to each handler.

Few things to keep in mind when making changes to the configuration:

- When you set '*active*' to **True** for specific handler, any logger using this configuration will have the handler added.
- Handler names must be the same as the ones in the **logging** module, including casing.
- All the required arguments passed to specific handler must be specified in the configuration. For example,
  if I were to add a `SocketHandler <https://docs.python.org/3.6/library/logging.handlers.html#sockethandler>`_,
  I will need to pass in *host* and *port*, like so:

.. code-block:: ini

    SocketHandler =
        active: True
        level: ERROR
        host: 127.0.0.9
        port: 3000

Adding a Config
~~~~~~~~~~~~~~~

To add a config, run the following command in the same project root:

.. code-block:: bash

    $ logme add my_new_configuration_name

Then you will see a new configuration added onto 'logme.ini'.

.. code-block:: ini

    [logme]
    level = DEBUG
    formatter = {asctime} - {name} - {levelname} - {message}
    StreamHandler =
        active: True
        level: DEBUG
    FileHandler =
        active: True
        level: DEBUG
        filename: None
    NullHandler =
        active: False
        level: NOTSET

    [my_new_configuration_name]
    level = DEBUG
    formatter = {asctime} - {name} - {levelname} - {message}
    StreamHandler =
        active: True
        level: DEBUG
    FileHandler =
        active: True
        level: DEBUG
        filename: None
    NullHandler =
        active: False
        level: NOTSET

Removing a Config
~~~~~~~~~~~~~~~~~

The same way as you add a config, removing a config is very easy too:

.. code-block:: bash

    $ logme remove my_new_configuration_name

With the above command, the target configuration will be removed from 'logme.ini' file.




Using Loggers in Your Project
-----------------------------
_____________________________________________________________________

To use loggers in your project, you can simply use *logme.log* as a decorator or call it as a method,
without having to configure each logger manually in your code.

 :red:`logme.log()` can accepts 3 optional arguments for customize your logger:
    * **scope**: the scope of your logger: *class*, *function* or *module*. You can omit this parameter for class and
      function. **this is required for module level logger**
    * **config**: the name of logging config specified in logme.ini, default would be the *logme* config
    * **name**: the name of the logger, default would be the __name__ of the file where you are calling logme.log, or using the logme.log decorator.



Logging for functions and methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For functions, you can simple just decorate the function/method in which you want to use the logger, like so:

.. code-block:: python

    @logme.log(config='my_custom_conf', name='custom_test_logger')
    def dummy_function_custom(name, logger=None):
        logger.info('test function logger with custom params')

        return logger, name


.. note:: Be sure to pass in the "logger" as a keyword argument, and you can assign it to None when defining the function



Logging for classes
~~~~~~~~~~~~~~~~~~~
For classes, you can also use the decorator, and an attribute *self.logger* will be available.

.. code-block:: python

    @logme.log
    class MyAwesomeClass:
        def my_function(self, my_arg):
            self.logger.info('this is my log message')




logging for modules
~~~~~~~~~~~~~~~~~~~
Logging modules is slightly different from classes and functions, but it's just as straight forward.
*and remember, scope keyword argument must be passed in*

.. code-block:: python

    module_logger = logme.log(scope='module', name='my_module_logger')

