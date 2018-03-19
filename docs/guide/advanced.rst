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

If you are making a distributed or installable package, and you still want to include logging.
You can easy do this with logme package.

The following are the simple steps:

1. Have only the **NullHandler** set to '*active*' in your project root logme.ini file. This
   will ensure logging messages do not get output unless the configuration is changed.

2. In your __init__.py file, make a module logger, like so:

.. code-block:: python

    logger = logme.log(scope='module')

3. Import this logger throughout your project. Take note that this means the whole project will be
   logged with this single logger.


4. If user need to see the logging messages, they can then import the logger and change the configuration.
   There are two ways to reset the logging configuration, see below:

I: Using logme config name:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assuming if the user of the package also have initialized in their project root, you can reset the configuration
by directly passing in the configuration name with **config_name** argument.

**Example**:

.. code-block:: python

    from your_project import logger

    logger.reset_configuration(config_name='my_own_logger')



II: Using a config dictionary:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Configuration can also be passed in as a dictionary with **config** argument.

**config structure:**

.. code-block:: python

    {
        'level': 'string',
        'format': 'string',
        'handler1': {
            'active': True,
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
                "StreamHandler": {
                    "active": True,
                    "level": "DEBUG",
                },
                "FileHandler": {
                    "active": True,
                    "level": "DEBUG",
                    "filename": "/var/log/mylog.log",
                },
            }

    }
    logger.reset_configuration(config=config)
