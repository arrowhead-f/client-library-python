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
 - Support for the TOKEN security modes (access policy):

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

