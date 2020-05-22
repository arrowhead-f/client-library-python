# ARROWHEAD CLIENT PYTHON LIBRARY
This is a library for the creation of client service providers and consumer for the [Arrowhead Framework](www.arrowhead.eu), a service-oriented framework developed for industrial automation.

## About
The Arrowhead Client Python Library is a library to make it easy to create your own Arrowhead Framework systems and services in Python.
This library provides classes that interface with the [Arrowhead Core Systems](https://github.com/arrowhead-f/core-java-spring), and uses Flask to provide services.

### Development status
This library has not yet reached a stable development version, and a lot will change.
Currently, it is working, but it's still missing many crucial features, such as:
 - Error handling
 - Logging
 - Testing
 - Support for the following core services
   - Eventhandler
   - Gateway
   - Gatekeeper
 - Support for the following security modes (access policies):
   - Token security
   - Insecure security

As more Arrowhead Core Systems mature and are added to the official docker container, those will be added to this list.

### External Depencies
To run an Arrowhead system you need to have the Arrowhead core systems up and running, and the correct certificates need to be provided.
A guide on how to create your own certificates can be found on the [Arrowhead github](https://github.com/arrowhead-f/core-java-spring/blob/master/documentation/certificates/create_client_certificate.pdf).

### Requirements
 - Python 3.7 or higher
 - Requests
 - Flask
 - Gevent

## How To Use
Install the library with `pip install arrowhead-client`.

### Providing Services
To provide services, import the `ProviderSystem`.
Services can be added to the provider  with the `provided_services` decorator.
The `provided_services` decorator will create a service, and register the service with the provider.
Then when the provider is started, using the `run_forever` method, the provider will automatically register the service with the service registry.

#### Code Example
```python
import datetime
from arrowhead_client.system.provider import ProviderSystem

# Create provider
time_provider = TimeProvider(
		'time_provider',
		'localhost',
		1337,
		'',
		keyfile='certificates/time_provider.key'
		certfile='certificates/time_provider.crt')

# Add service
@time_provider.provided_service('echo', '/time/echo', 'HTTP-SECURE-JSON', 'GET')
def echo():
	return {'now': str(datetime.datetime.now())}

if __name__ == '__main__':
	time_provider.run_forever()

```

### Consuming Services
To consume services, use the `ConsumerSystem`.
To find a consumed service, you first register a service definition using the `add_consumed_services` method.
When the `ConsumerSystem` is started initialized, it queries the orchestrator and will register the first orchestrated service.
That service is then consumed using the `consume_service` method.

The orchestration query _will fail_ if the orchestrator does not return a service, and crash as a consequence.
The plan is to make this robust later.

#### Code Examples
```python

from arrowhead_client.system.consumer import ConsumerSystem

time_consumer = ConsumerSystem(
		'consumer_test',
		'localhost',
        '1338',
        '',
        'certificates/consumer_test.key',
        'certificates/consumer_test.crt')

# Add orchestration rules
time_consumer.add_orchestration_rule('echo', 'GET')

if __name__ == '__main__':
    # Consume service provided by the 'get_time' rule
    echo = time_consumer.consume_service('echo')
    print(echo['echo'])

```

