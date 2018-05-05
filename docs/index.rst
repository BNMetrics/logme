.. logme documentation master file, created by
   sphinx-quickstart on Tue Feb 27 18:29:57 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

================================
Logme - Python Logging Made Easy
================================

.. image:: https://badge.fury.io/py/logme.svg
    :target: https://pypi.org/project/logme/

.. image:: https://travis-ci.org/BNMetrics/logme.svg?branch=master
    :target: https://travis-ci.org/BNMetrics/logme

.. image:: https://codecov.io/gh/BNMetrics/logme/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/BNMetrics/logme

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Logme is a Python package that makes logging simple and robost. If you have found
logging in Python not so straight forward, download this package and give it a try! :)


v1.1.0 Updates
--------------

**logme** is now capable of having the same type of handlers with different configuration in ``logme.ini``

To upgrade to the latest version, first you will need to install the latest version of **logme** package

.. code-block:: bash

    $ pip3 install logme --upgrade


Then upgrade the ``logme.ini``, run the following command in your project directory where logme.ini resides.

.. code-block:: bash

    $ logme upgrade


.. note:: v1.1.0+ is backwards compatible, so if you still have the previous version of ``logme.ini``, you will not be affected.


In a Nutshell
-------------
_____________________________________________________________________

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


The User Guide
--------------
_____________________________________________________________________

.. toctree::
   :maxdepth: 2

   guide/quickstart
   guide/advanced



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
