.. _eclipse-arrowhead:

===============================
The Eclipse-Arrowhead Framework
===============================

The Eclipse-Arrowhead Framework is a service-oriented, system-of-systems architecture framework designed
with the demands of Industry 4.0 in mind.
The goals of the framework is no enable seamless interoperability between heterogeneous systems in terms of
operation and semantics.

-------------
Core Concepts
-------------

The Eclipse-Arrowhead Framework is based on a couple of core concepts, namely the *local cloud*, *system*, and *service*.

Systems
^^^^^^^

An *Arrowhead system* is a software system that supports the use of the Eclipse-Arrowhead framework, which means it
it can utilize the core services, and it provides or consumes a service from another system.

Services
^^^^^^^^

A *service* is a connection that can be established by two Arrowhead systems, for the means of exchanging information.
For example, a temperature sensor could provide a service called ``temperature``, and a climate controller could consume that service.
In this case, the temperature sensor is called a *service provider*, and the climate controller is called a *service consumer*.

Many systems will likely both provide and consume services simultaneously, and what system is considered a consumer or
provider is dependent on the service in question.

Local Clouds
^^^^^^^^^^^^

An *Arrowhead Local Cloud* is a collection of client Arrowhead systems and the three mandatory core systems:
The *Service Registry*, the *Orchestrator*, and the *Authorization* system.
These three systems serve three important rolls in the architecture, namely:

* Registration and Lookup - A system can register it's services at the Service Registry, which allows them to be discovered by other systems in the local cloud.
* Orchestration and Late Binding - When a system enters the local cloud it will not know any endpoints besides the core services' (Or maybe not even them, see Onboarding.)
  The Orchestrator serves as the central location where systems can get *orchestration rules*, i.e. rules that tells a system where the services it wants to consume are.
  These rules are controlled by the operator of the local cloud, who can thereby exert control over otherwise independent systems.
* Security and Access Control - Some systems might not be allowed to communicate due to security reasons, or they might need to prove that they are allowed to consume certain services.
  The Authorization system does both things, first it contains a list of what services a system can consume, and it also generates tokens that can validate that a system is allowed to consume another's services.

------------
Core systems
------------

As previously mentioned, an Arrowhead local cloud contains at least the three mandatory core systems.
Click each link to learn more about them and the core services they provide.

.. toctree::
   :maxdepth: 2
   :caption: Mandatory Core Systems

   service-registry
   orchestrator
   authorization

In addition to the mandatory core systems, the Arrowhead Framework also specifies many non-mandatory core systems,
which provide powerful functions useful both within and between local clouds.

.. toctree::
   :maxdepth: 2
   :caption: Non-Mandatory Core Systems

   event_handler