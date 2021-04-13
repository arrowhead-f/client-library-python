.. _orchestrator:

============
Orchestrator
============

The Orchestrator is where a system go to find the services it wants to use.
The Orchestrator works as a repository of orchestration rules, which describes that consumer A gets to consume service S of provider P, using interface I.
An administrator of the local cloud can change these rules to change the overall behaviour of the local cloud.

The Orchestrator provides only one service, Orchestration.

Orchestration
-------------

The Orchestration service provides the endpoints as described above, but it also have a lot of options, including two different orchestration modes, inter-cloud orchestration, and more.
The Orchestration service is consumed using the :py:meth:`~arrowhead_client.client.ArrowheadClient.add_orchestration_rule` method of the :py:class:`~arrowhead_client.client.ArrowheadClient` class.

Further Reading
---------------

For a more detailed look into the Orchestration system and the Orchestration service can be found in the `official Eclipse-Arrowhead documentation <https://github.com/eclipse-arrowhead/core-java-spring#orchestrator>`_.