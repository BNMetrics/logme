.. _quickstart:

Quickstart
==========


Installation
------------
_____________________________________________________________________

To install the latest version of logme via **pip**:

::

    $ pipenv install logme
    ✨🍰✨

Configurations
--------------
_____________________________________________________________________

Initialization
~~~~~~~~~~~~~~

.. _init:

To use logme for your project, you will need to cd into your project root:

.. code-block:: bash

    $ cd /path/to/project_root

    $ logme init

Then you will see a configuration file 'logme.ini' created, it looks like this:

.. code-block:: ini

    [colors]
    CRITICAL =
       color: PURPLE
       style: BOLD
    ERROR = RED
    WARNING = YELLOW
    INFO = None
    DEBUG = GREEN

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

This is the file where you add configurations for your logging. In the above example:
   - ``[colors]`` is the color and styling configuration for loggings output to the terminal.
     See configuration details :ref:`here <colors>`.
   - ``[logme]`` is the master configuration for the loggers, and it cannot be removed.


Each block of configuration is independent, and you can apply the same configuration section to different loggers. You can have as many of them as you like.

.. note:: The top level ``level`` and ``formatter`` are master level handler configurations.
   This means if the level or/and formatter on each handler ('steam', 'file', 'null' block in the example) are not specified,
   the handlers will use the master level ones.

   With that said, ``level`` and ``formatter`` can be configured on handler level by adding these to each handler.

Few things to keep in mind when making changes to the configuration:

- When you set ``'active'`` to **True** for specific handler, any logger using this configuration will have the handler added.
- keys such as 'stream, file, null' are the name you can assign to handlers, each name much be unique.
- ``'type'`` must be the same as the ones in the **logging** module, e.g ``StreamHandler``, and it is **case sensitive**.
- All the required arguments passed to specific handler must be specified in the configuration. For example,
  if I were to add a `SocketHandler <https://docs.python.org/3.6/library/logging.handlers.html#sockethandler>`_,
  I will need to pass in *host* and *port*, like so:

.. code-block:: ini

    socket =
        type: SocketHandler
        active: True
        level: ERROR
        host: 127.0.0.9
        port: 3000


.. _colors:

Color Configuration
~~~~~~~~~~~~~~~~~~~

As you can see from the example in the :ref:`previous section <init>`, the colors configured based on the level of logging messages.
Each level can be configured with: **color**, **style** and **bg** (background).

In the example, ``CRITICAL`` level is being configured with both **color** and **style**. You can also add background color, like so:

.. code-block:: ini

    [colors]
    CRITICAL =
       color: PURPLE
       style: BOLD
       bg: BLUE
    ERROR = RED
    WARNING = YELLOW
    INFO = None
    DEBUG = GREEN

When you assign a single value to the level, it will automatically be interpreted as foreground colors. For example in ``ERROR``,  ``WARNING``,
``INFO`` and ``DEBUG``. Assigning styles as single value (for example, ``INFO=BOLD``) will cause an error.

If you want to assign only style or background to the specific level, you can configure it like so in the ``ERROR`` and ``WARNING`` section below:

.. code-block:: ini

    [colors]
    CRITICAL =
       color: PURPLE
       style: BOLD
    ERROR =
       style: BOLD
    WARNING =
       bg: YELLOW
    INFO = None
    DEBUG = GREEN


.. note:: ``[colors]`` configuration will apply to all loggers, and there should only be one color configuration in ``logme.ini`` file.


**Color Config Reference**
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Available Colors and BG Colors:
    - Black, Red, Green, Yellow, Blue, Purple, Cyan, White

Available Styles:
    - Underline, Bold




Adding a logger Config
~~~~~~~~~~~~~~~~~~~~~~

To add a logger config, run the following command in the same project root:

.. code-block:: bash

    $ logme add my_new_configuration_name

Then you will see a new configuration added onto 'logme.ini'.

.. code-block:: ini

    [colors]
    CRITICAL =
       color: PURPLE
       style: Bold
    ERROR = RED
    WARNING = YELLOW
    INFO = None
    DEBUG = GREEN


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


    [my_new_configuration_name]
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

Removing a logger Config
~~~~~~~~~~~~~~~~~~~~~~~~

The same way as you add a config, removing a config is very easy too:

.. code-block:: bash

    $ logme remove my_new_configuration_name

With the above command, the target configuration will be removed from 'logme.ini' file.

.. note:: ``[logme]`` and ``[colors]`` cannot be removed.


Using Loggers in Your Project
-----------------------------
_____________________________________________________________________

To use loggers in your project, you can simply use *logme.log* as a decorator or call it as a method,
without having to configure each logger manually in your code.


Logging for functions and methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For functions, you can simple just decorate the function/method in which you want to use the logger, like so:

.. code-block:: python

    @logme.log(config='my_custom_conf', name='custom_test_logger')
    def dummy_function_custom(name, logger=None):
        logger.info('test function logger with custom params')

        return logger, name


.. note:: Be sure to pass in the ``logger`` as a keyword argument, and you can assign it to ``None`` when defining the function.
          This allows the logger object to be passed in the the function from the decorator.



Logging for classes
~~~~~~~~~~~~~~~~~~~
For classes, you can also use the decorator, and an attribute ``self.logger`` will be available.

.. code-block:: python

    @logme.log
    class MyAwesomeClass:
        def my_function(self, my_arg):
            self.logger.info('this is my log message')




logging for modules
~~~~~~~~~~~~~~~~~~~
Logging modules is slightly different from classes and functions, but it's just as straight forward.

**and remember, scope keyword argument must be passed in!**

.. code-block:: python

    module_logger = logme.log(scope='module', name='my_module_logger')




**Reference**:
~~~~~~~~~~~~~~

``logme.log(scope: str=None, config: str=None, name: str=None)``
     **parameters**:
        - ``scope``: the scope of your logger: *class*, *function* or *module*. You can omit this parameter for class and
          function. **this is required for module level logger**
        - ``config``: the name of logging config specified in logme.ini, default would be the *logme* config
        - ``name``: the name of the logger, default would be the __name__ of the file where you are calling logme.log, or using the logme.log decorator.


