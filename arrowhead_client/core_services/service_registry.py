#!/usr/bin/env python

import requests
from typing import Optional
from ..service import ConsumedHttpService
from ..core_service_responses import handle_service_query_response
from ..configuration import default_config as config

_serviceregistry = config['service_registry']

#TODO: The service definition is repeated, this dict should be a custom class
# where __getitem__() looks through a list of services. Or not, I'm not sure
services = {
    'register': ConsumedHttpService(
            service_definition='register',
            service_uri='serviceregistry/register',
            interface='HTTP-SECURE-JSON',
            address=_serviceregistry['address'],
            port=_serviceregistry['port'],
            http_method = requests.post),
    'query': ConsumedHttpService(
            service_definition='query',
            service_uri='serviceregistry/query',
            interface='HTTP-SECURE-JSON',
            address=_serviceregistry['address'],
            port=_serviceregistry['port'],
            http_method=requests.post,
            post_processing=handle_service_query_response),
    'unregister': ConsumedHttpService(
            service_definition='unregister',
            service_uri='serviceregistry/unregister',
            interface='HTTP-SECURE-TEXT',
            address=_serviceregistry['address'],
            port=_serviceregistry['port'],
            http_method=requests.delete)
}
