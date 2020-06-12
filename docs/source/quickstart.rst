Arrowhead Client library quickstart
===================================

.. warning::

    This document is a work in progress.

Setting up a local cloud
------------------------

On Linux
^^^^^^^^

TBW.

On windows
^^^^^^^^^^

TBW.

Getting a provider running
--------------------------

The provider provides services within a local cloud.
To get a provider running start by importing the client library.

.. literalinclude:: ../../examples/provider_app.py
    :language: python
    :lines: 4

Then we can create an application containing a system and provider.

.. literalinclude:: ../../examples/provider_app.py
    :language: python
    :lines: 6-12

To add a service, we decorate a function with the `provided_service` decorator, and the service information.

.. literalinclude:: ../../examples/provider_app.py
    :language: python
    :lines: 15-21

Everything is now inplace, we just need to start the application with the `run_forever` method.

.. literalinclude:: ../../examples/provider_app.py
    :language: python
    :lines: 23-24

This method will start the application, register the services with service registry and simply serve until we terminate
the app with ctrl+c.

And that's it! In 15 lines of code (6 if you make the code hard to read)
we have set up a provider and are currently running it!
Here is the full code listing for this example.

examples/provider_app.py
^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../../examples/provider_app.py
    :language: python


Getting a consumer running
--------------------------

It's just as easy to get a consumer going, we start in a similar way.

.. literalinclude:: ../../examples/consumer_app.py
    :language: python
    :lines: 4-12

Now, instead of adding a provided service, we tell it what service to consume with the `add_consumed_service` method.

.. literalinclude:: ../../examples/consumer_app.py
    :language: python
    :lines: 14

To consume the service, we only need to call the `consume_service` method with the name of the service we want to consume.

.. literalinclude:: ../../examples/consumer_app.py
    :language: python
    :lines: 16-18

And the full listing:

examples/consumer_app.py
^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../../examples/consumer_app.py
    :language: python

If you first start the provider application and then run the consumer application, the your terminal should print

.. code:: shell

    Hello, Arrowhead!

Beyond the tutorial
-------------------

Congratulations, you have created your first Arrowhead services and systems in using the arrowhead-client library!
This tutorial is meant to show you the basics of using the library without any bells and whistles, just a simple pair
of providers and consumers.

If you had trouble getting these examples up and running, please look at :ref:`tutorial_trouble`.
