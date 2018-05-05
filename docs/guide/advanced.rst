.. _advanced:

Advanced Usage
==============

CLI options
-----------
_____________________________________________________________________

In addition to the basic CLI commands showing in the `previous section <http://127.0.0.1:8000/guide/quickstart.html#configurations>`_,
there are options you can add to the commands which allow you to get your configuration faster.


Option that applies to all commands:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:--project_root, -p:
    Alternative to cd into the project root before using 'logme ini'. You can add this flag to specify the project root.
    This is where you want the logme.ini file to be located. Can be either relative or absolute path.

.. note:: If you use the -p flag with **logme init**, and if the destination directory does not exist,
          you can add a '*--mkdir*' or '*-mk*' flag to create the directory. '*--mkdir/-mk*' flag is only available for **logme init**.


Option that applies to 'logme init' and 'logme add config_name':
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:--level, -lvl:
    Master level for the logger configuration.


:--formatter, -f:
    Master level formatter of the logger configuration.

:--log-path, -lp:
    If you use a FileHandler for your logger, this is the log file path for the handler. This must be absolute path.





Logger Delegation
-----------------
_____________________________________________________________________

If you are making a distributed or installable package, and you still want to include logging without disrupting the user of your package.
You can easy do so with logme package.

The following are the simple steps:

1. Have only the **NullHandler** set to '*active*' in your project root logme.ini file. This
   will ensure logging messages do not get output unless the configuration is changed.

2. In your ``__init__.py`` file, make a module logger, like so:

.. code-block:: python

    logger = logme.log(scope='module')


3. Import this logger throughout your project. Take note that this means the whole project will be
   logged with this single logger.


4. If the package user need to include the logging messages from your package, they can then import the logger and change the configuration.
   There are two ways to reset the logging configuration, see below:


I: Using logme config name:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assuming if the user of the package also have initialized ``logme`` in their project root, you can reset the configuration
by directly passing in the configuration name with **config** argument.

**Example**:

.. code-block:: python

    from your_project import logger

    logger.reset_configuration(config='my_own_logger')



II: Using a config dictionary:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Configuration can also be passed in as a dictionary with **config_dict** argument.

**config structure:**

.. code-block:: python

    {
        'level': 'string',
        'format': 'string',
        'handler_name': {
            'active': True,
            'type': 'FileHandler'
            'level': 'string', # Optional
            'formatter': 'string', # Optional
            'handler_arg1': 'mixed', # This is the argument you pass into specific handler
            'handler_arg2': 'mixed',
        }
    }

**Example**:

.. code-block:: python

    from your_project import logger

    config = {
                "level": "DEBUG",
                "format": "{levelname}: {message}",
                "debug_stream": {
                    "type": "StreamHandler",
                    "active": True,
                    "level": "DEBUG",
                },
                "file_debug": {
                    "type": "FileHandler",
                    "active": True,
                    "level": "DEBUG",
                    "filename": "/var/log/mylog.log",
                },
            }

    }
    logger.reset_configuration(config_dict=config)



**Reference**:
~~~~~~~~~~~~~~

``reset_config(config: str=None, config_dict: dict=None, name: str=None):``
    **parameters**:
        - ``config``: (*optional*) configuration(ini file section) name from logme.ini
        - ``config_dict``: (*optional*) configuration dictionary
        - ``name``: (*optional*) The new name for the logger
    **notes**:
        - One of ``config_dict`` or ``config`` must be specified



Adhoc Config change
-------------------
_____________________________________________________________________

If you would like to change the logger configuration for specific logger, but do not want to change the config in ``logme.ini`` file,
especially if such change is small, and it only applies to one single logger. There are a few ways of doing this.

As previously mentioned in the **Logger Delegation** section, logging configuration can be reset after the creation of the logger
by calling ``reset_configuration() method``, however, this would mean resetting the entire config of the logger.

Instead of changing the whole config, You can also change only the level and the formatter of the logger or the individual handlers.


I: Changing ``master_level`` and ``master_formatter``:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``master_level`` and ``master_formatter`` are attributes of the logger object. These attributes applies to all the handlers in the logger,
if they are not being specified for each handler.

To change the master attributes, simply override them, like so:

**Example**:

.. code-block:: python


    @logme.log
    def my_awesome_logger(logger=None):
        logger.master_level = "ERROR"
        logger.master_formatter = "{funcName} :: {levelname} :: {message}"
        logger.info("This message won't be logged after level changing")

        return logger




II: Reconfiguring specific handlers:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of configuring ``master_level`` and ``master_formatter``, you can also change the configuration of specific handler by calling
``reconfig_handler()`` method.


**Example**:

.. code-block:: python


    @logme.log
    def changing_logger_level(logger=None):
        logger.reconfig_handler('stream', level='WARNING')

        return logger


    @logme.log
    def changing_logger_formatter(logger=None):
        logger.reconfig_handler('file', formatter='{funcName}::{message}')

        return logger



.. note:: Handler configuration change is only viable if your logger has one of each type of handler. The future plan
          is to assign names to each handler, so this will work with multiple handlers of the same type.


**Reference**:
~~~~~~~~~~~~~~

``reconfig_handler(handler_name: str, level: Union[str, int]=None, formatter: str=None)``
    **parameters**:
        - ``config_name``: **case sensitive**. Type of the handler, specified as a option key in ini file
        - ``level``: (*optional*) The new level to be set
        - ``formatter``: (*optional*) the new formatter to be set. '{' style.





Using Logme in Installable Package
-----------------
_____________________________________________________________________

When you make an ``pip`` installable package, you will need to ensure that ``logme.ini`` is installed alongside your package code
to python's ``site-packages/`` directory.

There are two options to make this happen, and for both of them you will need to include ``logme.ini`` in your **package root**(*where your source code is*) directory
instead of project root(*the same directory as your*``setup.py``).

It would look like this::

    myproject_root/
        mypackage_root/
            __init__.py
            myfile.py
            logme.ini
        setup.py


I. Using package_data in setuptool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the simplest way to include non-python files in your package, you only need to include  ``package_data`` argument in your ``setup.py``, like so:

.. code-block:: python

    setup(
        name='myproject',
        packages=find_packages(exclude=['tests*']),
        package_data={'': ['logme.ini']},
        version=1.0,
        description='My awesome package that is using logme',
        author='Jane doe',
        url='https://www.example.com',
        author_email='jane@example.com',
        license='Apache 2.0',
    )


I. Using ``MANIFEST.in``
~~~~~~~~~~~~~~~~~~~~~~~~

You can also utilizing ``MANIFEST.in`` to help you include ``logme.ini``. With this option, you will need to create a ``MANIFEST.in`` file in your **project root**.

Below is a sample ``MANIFEST.in`` file that includes logme.ini::

    include LICENCE README.rst logme.ini


Now in the ``setup.py`` you will need to add an additional argument: ``include_package_data=True`` instead of ``package_data``:

.. code-block:: python

    setup(
        name='myproject',
        packages=find_packages(exclude=['tests*']),
        include_package_data=True,
        version=1.0,
        description='My awesome package that is using logme',
        author='Jane doe',
        url='https://www.example.com',
        author_email='jane@example.com',
        license='Apache 2.0',
    )