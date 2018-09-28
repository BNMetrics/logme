=================================
Logme - Python Logging for Humans
=================================

.. image:: https://badge.fury.io/py/logme.svg
    :target: https://pypi.org/project/logme/

.. image:: https://travis-ci.org/BNMetrics/logme.svg?branch=master
    :target: https://travis-ci.org/BNMetrics/logme

.. image:: https://codecov.io/gh/BNMetrics/logme/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/BNMetrics/logme

.. image:: https://readthedocs.org/projects/logme/badge/?version=latest
    :target: https://logme.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Logme is a Python package that makes logging simple and robust. If you have found
logging in Python not so straight forward, download this package and give it a try! :)



V1.3.0 Updates
---------------------
``logme.ini`` file now supports custome ``datefmt`` and ``style``! Thanks to `@afunTW <https://github.com/afunTW>`_ suggestion! :)

Here is an example of how you can specify these parameters in your ``logme.ini`` configuration:

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

Note: Only top level ``master_formatter`` supports parameters as shown above, individual handler formatter will not.



Terminal Color Output
---------------------

**logme** supports color and styling output in the terminal!

The colors and style is **customizable** in ``logme.ini``, here is a screenshot of how it looks like in the terminal:


.. image:: http://logme.readthedocs.io/en/latest/_images/demo_color.png

To use color output in logme, make sure your logme package and ``logme.ini`` is `up-to-date <https://logme.readthedocs.io/en/latest/?badge=latest#upgrading>`_ if you are using a version before 1.2.0.

Check the configuration details `here <https://logme.readthedocs.io/en/latest/guide/quickstart.html#colors>`_.



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

To get started, head to the `quickstart <https://logme.readthedocs.io/en/latest/guide/quickstart.html>`_  page.

Installation
------------

::

    $ pipenv install logme
    ✨🍰✨


Documentation
-------------

You can find the documentation at https://logme.readthedocs.io/en/latest/ .
Give it a try!

