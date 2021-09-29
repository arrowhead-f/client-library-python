# CHANGELOG

## Version 0.5.0a

Unreleased

- `ArrowheadClient` supports multiple consumers, one per protocol.
  These are added by subclassing the `ArrowheadClient` and changing the `__arrowhead_consumers__` class attribute.
  The consumers are initialized at instance initialization when using the `ArrowheadClient.create(...)` constructor.
  However, if an instance is is initialized with `__init__` it will **not** use the `__arrowhead_consumers` attribute.
- Eventhandler supported through the following methods:
  - `ArrowheadClient.handle_event` is used to decorate a callback that acts on the received event.
  - `ArrowheadClient.publish_event` to publish events to the Event handler.
- `ArrowheadClient.consume_service` will now iterate through all orchestration rules and try to make a connection for each one. If none succeeds an error will be thrown.  
- The API is not stable and the names of the methods are subject to change without notice.

### (Known) Backwards incompatible changes
- `ArrowheadClient.__arrowhead_consumer__` changed name to `ArrowheadClient.__arrowhead_consumers__` to reflect that a client now supports multiple consumers.


Prior to version 0.5.0a
-----------------------

Only tales long forgotten may tell what changed in each version back in the dark days...