.. _quickstart:

===================================
Arrowhead Client library quickstart
===================================
.. warning::

    This library is a work in progress, and no api should be considered stable.

Prerequisites
-------------

 - Arrowhead_client library installed
 - Docker installed
 - Docker compose installed

Running the quickstart example
------------------------------

Setting up an Arrowhead local cloud can be a tricky process.
To simplify that process, this library provides an example directory that contains all necessary components to setup a local cloud.
You can access that folder by cloning the repository and navigating into the :code:`examples/quickstart` directory.

To start and setup the local cloud, run:

.. code-block:: shell-session

    python quickstart_setup.py

This script will start local cloud and setup the orchestration and authorization rules necessary to run the example files.

Getting a provider running
--------------------------

The provider provides services within a local cloud.
To get a provider running start by importing the client library.

.. literalinclude:: ../../../examples/quickstart/clients/provider.py
    :language: python
    :lines: 4

Then we can create an http client running in secure mode.

.. literalinclude:: ../../../examples/quickstart/clients/provider.py
    :language: python
    :lines: 6-13

To add a service, we decorate a function with the :code:`provided_service` decorator of the :code:`provider`.
The decorator takes as arguments the service definition, service uri, protocol and related method, payload format
and access policy, which is one of :code:`'NOT_SECURE'`, :code:`'CERTIFICATE'` and :code:`'TOKEN`.
For more information regarding access policies/security modes, see
:ref:`the user guide section on security <security-user-guide>` and `the Eclipse-Arrowhead documentation. <https://github.com/eclipse-arrowhead/core-java-spring#authorization>`_

.. literalinclude:: ../../../examples/quickstart/clients/provider.py
    :language: python
    :lines: 16-25

This example will return a simple JSON message when the client is accessed on :code:`https://127.0.0.1:7655/hello`,
using the token access policy.

The :code:`request` parameter in the previous example is necessary as it contains the request body.
The request body is ignored when the http method is get, but let's make another service that echoes any JSON
message it's given:

.. literalinclude:: ../../../examples/quickstart/clients/provider.py
    :language: python
    :lines: 27-38

In this example, the request body can be accessed as a :code:`dict` using the :code:`request.read_json()` method.

All that's left to do now is to run the provider, which we do by calling the :code:`run_forever()` method.

.. literalinclude:: ../../../examples/quickstart/clients/provider.py
    :language: python
    :lines: 40-41

This method registers the provider system and services, and then runs the underlying Flask application.
The output should look like this:

.. code-block::

    Service Registry entry with provider: (quickstart-provider, 127.0.0.1:7655) and service definition: hello-arrowhead already exists.
    Service Registry entry with provider: (quickstart-provider, 127.0.0.1:7655) and service definition: echo already exists.
    Started Arrowhead ArrowheadSystem
     * Serving Flask app "" (lazy loading)
     * Environment: production
       WARNING: This is a development server. Do not use it in a production deployment.
       Use a production WSGI server instead.
     * Debug mode: off
     * Running on https://127.0.0.1:7655/ (Press CTRL+C to quit)

And that's it! In 30 lines of code (or 11 if you make the code hard to read)
we have set up an Arrowhead provider with two services and are currently running it!
Here is the full code listing for this example.

``examples/quickstart/clients/provider.py``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../../../examples/quickstart/clients/provider.py
    :language: python

Next, we will create a consumer.

Getting a consumer running
--------------------------

It's just as easy to get a consumer going, we start similarly by importing the library and creating a client.

.. literalinclude:: ../../../examples/quickstart/clients/consumer.py
    :language: python
    :lines: 4-13

A difference between a provider and a pure consumer is that we need to set up the pure consumer first:

.. literalinclude:: ../../../examples/quickstart/clients/consumer.py
    :language: python
    :lines: 16-17

This method was also called by the provide inside the :code:`run_forever()` method.
The setup method enables the consumer to use the core services.

To consume a service, the consumer needs to get the orchestration rule from the orchestrator core system:

.. literalinclude:: ../../../examples/quickstart/clients/consumer.py
    :language: python
    :lines: 19

The first argument is the service definition, and the second is the http method used.

Then we can consume the service and print the response:

.. literalinclude:: ../../../examples/quickstart/clients/consumer.py
    :language: python
    :lines: 20-21

Let's do the same for the second service:

.. literalinclude:: ../../../examples/quickstart/clients/consumer.py
    :language: python
    :lines: 23-25

The output should then be

.. code-block::

    Hello, Arrowhead!
    ECHO

And the full listing:

:code:`examples/quickstart/clients/consumer.py`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../../../examples/quickstart/clients/consumer.py
    :language: python

If you first start the provider application and then run the consumer application, the your terminal should print

.. code:: shell

    Hello, Arrowhead!

Beyond the tutorial
-------------------

These examples show the basics of what the library will be able to do, with support for further protocols and features planned.
Try changing the functions in :code:`provider.py` a bit and see what happens.
If you want to add new services to the cloud, you need to set up orchestration and authorization rules.
I suggest taking a look at the `Arrowhead Management Tool <https://github.com/arrowhead-tools/mgmt-tool-js>`_
to do that.

Just note that the cloud used for this example only contains the mandatory core systems, i.e.
the service registry, orchestrator, and authorization systems.
If you want to use more core services, you need to set up your own local cloud,
which is outside the scope of this tutorial.

Quickstart help
---------------

This section will be filled with the various questions and issues people have with the quickstart.