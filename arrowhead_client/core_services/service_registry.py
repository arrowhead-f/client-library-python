from typing import Dict
from arrowhead_client.service import Service


#TODO: The service definition is repeated, this dict should be a custom class
# where __getitem__() looks through a list of services. Or not, I'm not sure
services: Dict[str, Service] = {
    'register': Service(
            service_definition='register',
            service_uri='serviceregistry/register',
            interface='HTTP-SECURE-JSON',),
    'query': Service(
            service_definition='query',
            service_uri='serviceregistry/query',
            interface='HTTP-SECURE-JSON',),
    'unregister': Service(
            service_definition='unregister',
            service_uri='serviceregistry/unregister',
            interface='HTTP-SECURE-TEXT',)
}
