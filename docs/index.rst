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


v1.2.0 Updates
--------------
_____________________________________________________________________

**logme** package now supports color and styling output in the terminal!

The colors and style is **customizable** in ``logme.ini``, here is a screenshot of how it looks like in the terminal:


.. image:: _images/demo_color.png

To use color output in logme, make sure your logme package and ``logme.ini`` is :ref:`up-to-date <upgrading>`.

Check the configuration details :ref:`here <colors>`.


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


.. _upgrading:

Version Upgrades
----------------
_____________________________________________________________________

For all versioning changes, your ``logme.ini`` file should also be changed for the new features to take place in your project.
``logme`` package makes the upgrading of versions simple with only two steps:


I. Upgrade to latest version of Logme:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ pip3 install logme --upgrade


II. Upgrade ``logme.ini`` using the following command:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ logme upgrade


.. note:: Each newer version is backwards compatible, so if you still have the previous version of ``logme.ini`` without upgrading, you will not be affected.



The User Guide
--------------
_____________________________________________________________________

.. toctree::
   :maxdepth: 2

   guide/quickstart
   guide/advanced
   guide/changelog



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
