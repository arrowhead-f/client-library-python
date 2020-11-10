Security settings
=================

The :code:`ArrowheadHttpClient` supports the CERTIFICATE and NOT_SECURE security modes.

CERTIFICATE mode
^^^^^^^^^^^^^^^^
To use the CERTIFICATE mode, provide a certfile and keyfile to the constructor.
If you're using a pkcs12 keystore, it needs to be converted to a certfile and keyfile first.

Example:

.. code-block:: python

    ArrowheadHttpClient(
        system_name='Secure',
        address='127.0.0.1',
        port=1337,
        keyfile='path/to/secure.key',
        certfile='path/to/secure.crt',
    )

NOT_SECURE mode
^^^^^^^^^^^^^^^
To use the NOT_SECURE mode, don't provide any certfile or keyfile.

Example:

.. code-block:: python

    ArrowheadHttpClient(
        system_name='Insecure',
        address='127.0.0.1',
        port=1338
    )

TOKEN mode
^^^^^^^^^^
The python client does not yet support the TOKEN security mode.