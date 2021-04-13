.. _service-registry:

================
Service Registry
================

The first mandatory core system is the *service registry* whose responsibility is summarized as

    "[The Service Registry is] Responsible for registering and enabling discovery of registered services."

    -- IoT Automation: Arrowhead Framework [1].

It does this through the use of 3 core services:
 * Service Registration
 * Service Unregistration
 * Service Query

Service Registration
--------------------

The service registration service is the place where systems can register their services, which makes them visible for other services.
This service is most often consumed during system setup, but might also be used during runtime if the system got updated.

Service Unregistration
----------------------

The opposite of the service unregistration service, which means this is where systems unregister their services.
All registered services must be unregistered when a system shuts down, but this service can also be called when a system is upgraded.

Service Query
-------------

The service query service exists to let other systems discover services in the local cloud.
However, that information will most often come from the orchestration system as part of the orchestration process, so this service should rarely be called, for example during startup using the onboarding procedure.

Further reading
---------------

A more detailed explanation of the Service Registry can be found in the official `Eclipse Arrowhead documentation <https://github.com/eclipse-arrowhead/core-java-spring#service-registry>`_

References
----------

 1. IoT Automation: Arrowhead Framework, edited by Jerker Delsing, Taylor & Francis Group, LLC (2017).