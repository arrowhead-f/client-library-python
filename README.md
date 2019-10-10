# ARROWHEAD CLIENT PYTHON LIBRARY
This is a library for the creation of client service providers and consumer for the [Arrowhead Framework](www.arrowhead.eu), a service-oriented framework for industrial automation.

## Installing Arrowhead
This library currently supports an older version of Arrowhead.
To install the framework, go [here](https://github.com/arrowhead-f/core-java/releases/tag/4.1.0), download debian\_packages.zip, then read the README [here](https://github.com/arrowhead-f/core-java).

### TO DO
Update this library to support Arrowhead 4.1.3

## About This Library
### Requirements
 - Python 3.7
 - Requests
 - Flask

#### TO DO
Make sure to specify depency versions

### Components
#### Arrowhead System
The *ArrowheadSystem* class contains four fields:
 - **systemName**
 - **address**
 - **port**
 - **authenticationInfo**.
This class is used as a simple information container for the *ServiceProvider* and *ServiceConsumer* classes, with the class entire class corresponding to a field in the various core service request forms.

#### Service Provider
The *ServiceProvider* class provides services and is based on the Flask library.
To implement a *ServiceProvider*, it needs a **service_uri**, **provider_system**, and **consumer_system**.
Once instantiated, service methods can be added with the **add_route** method, and finally the service can be run by calling the **run** method.

##### Authentication
While this library currently doesn't support secure core systems, the authentication system still needs to have a say in things.
Taking inspiration from the Java client skeletons (and an attempt to avoid having to mess around in mysql), the first time a provider is run it needs to be run with **run(auth=True)**.
This will give the authentication system a rule telling it that the **consumer_system** can indeed consume the service provided.
Though one could mess around with the authentication tables or use the management tool instead, I chose the easy route.

#### Service Consumer
The *ServiceConsumer* class is similar to the provider class.
To consume a service, call the **consume** method with a **service_name** and **service_method**.
The *ServiceConsumer* will then make a service request to the Orchestrator, and consume the service if it finds one.

##### TO DO
 - Implement a cache storing consumed services

