import requests
from arrowhead_system import ArrowheadSystem

class ServiceConsumer():
    def __init__(self,
            consumer_name = 'Default',
            address = 'localhost',
            port = '8080',
            authentication_info = '',
            consumer_system = None,
            requested_service = {},
            orchestration_flags = {},):
        if consumer_system:
            self.system = consumer_system
        else:
            self.system = ArrowheadSystem(consumer_name, 
                    address, 
                    port, 
                    authentication_info)
        self.req_service = requested_service
        self.orch_flags = orchestration_flags

    @property
    def system_name(self):
        return self.system.system_name

    @property
    def address(self):
        return self.system.address

    @property
    def port(self):
        return self.system.port

    def service_request_form(self, 
            requested_service = {},
            orchestration_flags = {}):
        service_request_form = {
                'requesterSystem': {
                    'systemName': self.name,
                    'address': self.host,
                    'port': self.port,
                    'authentificationInfo': 'null'
                    },
                'requestedService': requested_service,
                'orchestrationFlags': orchestration_flags,
                'preferredProviders': {},
                'requestedQoS': {},
                'commands': {}
                }

if __name__ == '__main__':
    consumer = ServiceConsumer()
    a = consumer.system_name
    print(a)

    
