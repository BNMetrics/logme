================================
Logme - Python Logging Made Easy
================================

.. image:: https://travis-ci.org/BNMetrics/logme.svg?branch=master
    :target: https://travis-ci.org/BNMetrics/logme



Logme is a Python package that makes logging simple and robost. If you have found
logging in Python not so straight forward, download this package and give it a try! :)


In A Nutshell
-------------

If you have a function you want to log, you can do this in your python file:

.. code-block:: python

    import logme


    @logme.log
    def my_awesome_function(my_arg, logger=None):
        logger.info('this is my log message')
        """rest of the function"""


You can do the same with classes too:

.. code-block:: python

    import logme


    @logme.log
    class MyAwesomeClass:
        def my_function(self, my_arg):
            self.logger.info('this is my log message')



pretty nice right? :)

Installation
------------

To install logme:

.. code-block:: bash

    $ pip3 install logme


Specifications
--------------

Getting Started
~~~~~~~~~~~~~~~
To get logme started, you will need to cd into your project root and type:

.. code-block:: bash

    $ logme init

Then you will see a configuration file 'logme.ini', it looks like this:

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

And this is where you configure your loggers, and each block of configuration are independent,
you can have as many of them as you like.

**level** and **formatter** are at the master level handler configurations. This means if the level and formatter on
each handler are not specified, the handlers will use the master level ones. To customize each handler,
simple edit the logme.ini file.


To add a config, do this:

.. code-block:: bash

    $ logme add my_configuration_here


Using Logger in Your Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*logme.log()* can accepts 3 optional arguments for customize your logger:
    * scope: the scope of your logger: *class*, *function* or *module*. You can omit this parameter for class and
      function. **this is required for module level logger**
    * config: the name of logging config specified in logme.ini, default would be the *logme* config
    * name: the name of the logger, default would be the __name__ of the file where you are calling logme.ini


**logging for functions and methods**
For functions, you can simple just decorate the function/method in which you want to use the logger, like so:

.. code-block:: python

    @logme.log(config='my_custom_conf', name='custom_test_logger')
    def dummy_function_custom(name, logger=None):
        logger.info('test function logger with custom params')

        return logger, name


*Be sure to pass in the "logger" as a keyword argument, and you can assign it to None when defining the function*


**logging for classes**
For classes, you can also use the decorator, and an attribute *self.logger* will be available.

.. code-block:: python

    @logme.log
    class MyAwesomeClass:
        def my_function(self, my_arg):
            self.logger.info('this is my log message')



**logging for modules**
Logging modules is slightly different from classes and functions, but it's just as straight forward.
*and remember, scope keyword argument must be passed in*

.. code-block:: python

    module_logger = logme.log(scope='module', name='my_module_logger')


Advanced Usage - Delegation
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Assuming you are making a distributed package, and you still want to include logging,
but you want to give the user the freedom to configure the logger. Follow these steps:

1. Have only the NullHandler active in your project root logme.ini file.
2. In your __init__.py file, make a module logger, like so:

.. code-block:: python

    logger = logme.log(scope='module')

3. Import this logger throughout your project.
4. When user need to see the logging messages, they can then import the logger and change the configuration.

.. code-block:: python

    from your_project import logger

    # assuming if the importer also has logme installed and initialized
    logger.reset_configuration(config_name='my_own_logger')

    # if not, a configuration dictionary can also be passed in this format:
    config = {
                "level": "DEBUG",
                "format": "{levelname}: {message}",
                "StreamHandler": {
                    "level": "DEBUG",
                },
                "FileHandler": {
                    "level": "DEBUG",
                    "filename": "/var/log/mylog.log",
                },
            }

    }
    logger.reset_configuration(config=config)


