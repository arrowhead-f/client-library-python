TODO-list
=========

Quality of Life
^^^^^^^^^^^^^^^

- Make it easy to provide and consume services simultaneously.

Service consumation
^^^^^^^^^^^^^^^^^^^

- Error handling when service could not be consumed.

Service Registry
^^^^^^^^^^^^^^^^

- Error handling when registrating and unregistrating a service.

Orchestration
^^^^^^^^^^^^^

- Error handling when no services are returned from orchestration request.
- Support for multiple returned services from orchestration request.
- Give proper support for orchestration flags, current praxis is to leave that field empty which defaults to using the :code:`overrideStore` flag.

Security
^^^^^^^^

- Implement the TOKEN security mode.

Logging
^^^^^^^

- Implement logging for:
    - Service registration errors.
    - Orchestration error.
    - Service consumation errors.