.. _security-user-guide:

===================================
Security in the Arrowhead Framework
===================================

Security in the Arrowhead Framework is established using a combination of TLS and `JWT-based <https://jwt.io/introduction>`_ token authorization.

Security Modes
^^^^^^^^^^^^^^

An :py:class:`~arrowhead_client.client.ArrowheadClient` can be run in two different security modes, :py:enum:mem:`~arrowhead_client.constants.Security.INSECURE` mode and :py:enum:mem:`~arrowhead_client.constants.Security.SECURE` mode.
An ``ArrowheadClient`` must be run in the same security mode as the local cloud it is in, as the ``SECURE`` mode enables TLS.
``INSECURE`` mode should only be run during testing and prototyping, and ``SECURE`` mode must be used in actual production local clouds.

Access Policies
^^^^^^^^^^^^^^^

:py:class:`~arrowhead_client.client.ArrowheadClient` objects support the ``CERTIFICATE``, ``UNRESTRICTED``,
and ``TOKEN`` access policies for services.
Here we only explain what the policies are used for and how to enable and use them.
For an explanation on how they work, go read about the :ref:`authorization-system`.

--------------------------
Unrestricted Access Policy
--------------------------

To make services use the ``UNRESTRICTED`` access policy, you simply don't provide a cert- or keyfile
to the ArrowheadClient providing those services.
By not providing both a cert- and keyfile, the client will run in ``INSECURE`` mode.
``INSECURE`` mode ensures that all provided services will use the ``UNRESTRICTED`` access policy
and that the client can only consume services with ``UNRESTRICTED`` access.

.. warning::

    The ``UNRESTRICTED`` access policy should only be used during testing and prototyping and never in production.

.. note::

    Even if a local cloud is using ``UNRESTRICTED`` access, you need to set both orchestration and **authorization**
    rules. The Orchestrator will ignore an orchestration rule if the equivalent authorization rule is not set.

Example:

.. code-block:: python

    from arrowhead_client.client import SyncClient

    example_client = SyncClient.create(
        system_name='Insecure',
        address='127.0.0.1',
        port=1338
    )

    print(example_client.secure)
    # False

-------------------------
Certificate Access Policy
-------------------------
The ``CERTIFICATE`` access policy is one of two policies that can be used when the client is running in ``SECURE`` mode,
which is enabled by providing **both** the **certfile** and **keyfile**.
Then, given a client that runs in ``SECURE`` mode, we can specify that a provided service should use the ``CERTIFICATE``
access policy when creating it using the :py:meth:`arrowhead_client.client.ArrowheadClient.provided_service` method or
:py:func:`arrowhead_client.client.provided_service` decorator.
Running a client in ``SECURE`` mode will enable the consumption of services using both the ``CERTIFICATE`` and ``TOKEN``
access policies.

Example:

.. code-block:: python
    :emphasize-lines: 7, 8, 17

    from arrowhead_client.client import SyncClient

    example_client = SyncClient(
        system_name='Secure',
        address='127.0.0.1',
        port=1337,
        keyfile='path/to/secure.key',
        certfile='path/to/secure.crt',
    )

    @example_client.provided_service.create(
            service_definition='secure_echo',
            service_uri='secure/echo',
            protocol='HTTP',
            method='GET',
            payload_format='JSON',
            access_policy='CERTIFICATE',
    )
    def secure_echo(request):
        return 'ECHO'

.. _token-access-policy:

-------------------
Token Access Policy
-------------------

.. caution::

    The ``TOKEN`` access policy works out-of-the-box with the :py:class:`arrowhead_client.client.SyncClient`, but
    not with the :py:class:`arrowhead_client.client.AsyncClient`.
    With the ``AsyncClient``, you will need to use a reverse proxy that provides the consumer certificate as an HTTP header,
    but that functionality is not yet implemented.
    The reason for this is that the ASGI standard which the Provider is built upon does not forward the certificate to the application.
    Once that is implemented in the standard and Uvicorn updates to support it, the ``TOKEN`` access policy will work
    with the ``AsyncClient`` without hassle.


While the ``CERTIFICATE`` does enable the use of TLS, any system with a valid certificate could consume the service.
The ``TOKEN`` access policy allows the provider to **authenticate** the consumer and make sure the consumer was given
permission to consume the service by the Authorization system.
You use the ``TOKEN`` access policies the same way you use the ``CERTIFICATE`` access policy, except that you specify
the ``TOKEN`` access policy:

.. code-block:: python
    :emphasize-lines: 17

    from arrowhead_client.client import SyncClient

    example_client = SyncClient.create(
        system_name='Secure',
        address='127.0.0.1',
        port=1337,
        keyfile='path/to/secure.key',
        certfile='path/to/secure.crt',
    )

    @example_client.provided_service(
            service_definition='token_data',
            service_uri='secure/token',
            protocol='HTTP',
            method='GET',
            payload_format='JSON',
            access_policy='TOKEN',
    )
    def secure_echo(request):
        return {"access policy": "TOKEN"}

Summary
^^^^^^^

What access policies can be used with what security mode is summarized in this table

.. table:: Access Policy vs Security mode

    +------------------+-------------+---------------------------------------------------+
    |                  | TLS enabled | Allowed access policy                             |
    |  Client security |             |                                                   |
    |  mode            |             +-------------------+-----------------+-------------+
    |                  |             |  ``UNRESTRICTED`` | ``CERTIFICATE`` | ``TOKEN``   |
    +------------------+-------------+-------------------+-----------------+-------------+
    | ``INSECURE``     | No          |     Yes           |     No          |   No        |
    +------------------+-------------+-------------------+-----------------+-------------+
    | ``SECURE``       | Yes         |     No            |     Yes         |   Yes       |
    +------------------+-------------+-------------------+-----------------+-------------+