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
 - Python 3.7
 - Requests
 - Flask

## How To Use
Currently, you need to create separate systems for providers and consumers, a system cannot easily do both.
It is possible to do both, but it is not clean.

### Providing Services
To provide services, use the `ProviderSystem` from the `arrowhead_system.system.provider` module.
Services can be added to the provider  with the `provided_services` decorator.
The `provided_services` decorator will create a service, register the service with the provider. 
Then when the provider is started, the provider will automatically register the service with the service registry.

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
To consume services, use the `ConsumerSystem` from the `arrowhead_client.system.consumer` module to create a consumer system.
The `add_consumed_services` method is used to query the orchestrator and to set up the consumer to consume the service.

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

