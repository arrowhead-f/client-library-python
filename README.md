# ARROWHEAD CLIENT PYTHON LIBRARY
This is a library for the creation of client service providers and consumer for the [Arrowhead Framework](www.arrowhead.eu), a service-oriented framework for industrial automation.

## About
The Arrowhead Client Python Library is a library to make it easy to create your own Arrowhead Framework systems and services in Python.
This library provides classes that interface with the [Arrowhead Core Systems](https://github.com/arrowhead-f/core-java-spring), and uses Flask to provide services.

### Development status
This library is currently in **alpha**, the basic pieces are in place but the specific interfaces are not yet finalized.
Many things will change between this version and the first release.

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
To provider services, use the `ProviderSystem` from the `arrowhead_system` module.
Services can be added to the provider by decorating a function with the `add_service`, inspired by Flask's `add_route` method.
The `add_service` method will register the service in the provider, and when the provider is started it will automatically register the service with the service registry.

#### Code Example
```python
import datetime
from arrowhead_client.arrowhead_system import ProviderSystem
from arrowhead_client.provider import provided_service
from flask import request
#from source.service_provider import ServiceProvider

class TimeProvider(ProviderSystem):
    def __init__(self, *args, **kwargs):
       ProviderSystem.__init__(self, *args, **kwargs)
       self.format = '%H:%M:%S'

if __name__ == '__main__':
    # Create provider
    time_provider = TimeProvider.from_properties('examples/time_provider.properties')

    # Register services
    @time_provider.add_service('time', '/time', 'HTTP-SECURE-JSON')
    def get_time():
        return datetime.datetime.now().strftime(time_provider.format)

    @time_provider.add_service('format', '/time/format', 'HTTP-SECURE-JSON', ['POST'])
    def change_format():
        data = request.data

        time_provider.format = data.decode()

        return data

    # Run provider until shutdown
    time_provider.run_forever()
```

### Consuming Services
To consume services, use the `ConsumerSystem` to create a consumer.
The `add_orchestration_rule` method is used to query the orchestrator and to set up the consumer to easily consume the service provided by the orchestrator.

#### Code Examples
```python
from arrowhead_client.arrowhead_system import ConsumerSystem

time_consumer = ConsumerSystem('consumer_test',
                                  'localhost',
                                  '1338',
                                  '',
                                  '127.0.0.1',
                                  '8443',
                                  'certificates/consumer_test.key',
                                  'certificates/consumer_test.crt')

# Add orchestration rules
time_consumer.add_orchestration_rule('get_time', 'GET', 'time')
time_consumer.add_orchestration_rule('change_format', 'POST', 'format')

if __name__ == '__main__':
    # Consume service provided by the 'get_time' rule
    time = time_consumer.consume('get_time')
    print(time.text)
    input()
    # Consume service provided by the 'change_format' rule
    time_consumer.consume('change_format', payload='%S:%M:%H')
    # Consume service provided by the 'get_time' rule
    time = time_consumer.consume('get_time')
    print(time.text)
```

