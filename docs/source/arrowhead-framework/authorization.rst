.. _authorization-system:

=========================
Authorization System
=========================

The Authorization system provide access control through two means: authorization rules and the :ref:`Token access policy <token-access-policy>`.
Authorization rules are similar to orchestration rules in that there needs to be an orchestration rule in place for a provider and consumer to communicate.
However, as said earlier these are to provide access control and not orchestration.
This means that orchestration and authorization rules work orthogonally, and can in principle be controlled by two different administators, one in charge of production and one in charge of security.
Thus authorization rules provide an extra layer of control.

The token access policy can be used for even more granular control.
When it is used, the authorization system will provide a `JWT <jwt.io/introduction>`_ to the orchestrator which the consumer has to send to the provider.
The provider will use the JWT to verify that the consumer is allowed by the authorization system to consume the service.
Without the token access policy, any system with a valid certificate can consume the services of any system if they know the service endpoint, which can lead to security issues within a local cloud.

The authorization system provides only one service, the Public-key service.

Public-key
----------

The public key service serves a single purpose: to provide the authorization system certificate to providers, which enables them to use the Token access policy.
This services is called during client startup, which means that using the token access policy is as easy as using the simpler certificate access policy.

Further Reading
---------------

You can read more about the Authorization system in the `official Eclipse-Arrowhead documentation <https://github.com/eclipse-arrowhead/core-java-spring#authorization>`_.