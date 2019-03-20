import requests
from arrowhead_system import ArrowheadSystem

class ServiceConsumer():
    def __init__(self,
            name = 'Default',
            address = 'localhost',
            port = '8080',
            authentication_info = '',
            consumer_system = None,
            requested_service = {},
            orchestration_flags = {},
            service_registry = None):
        if consumer_system:
            self.system = consumer_system
        else:
            self.system = ArrowheadSystem(name, 
                    address, 
                    port, 
                    authentication_info)
        self.req_service = requested_service
        self.orch_flags = orchestration_flags

        assert service_registry

    @property
    def system_name(self):
        return self.system.systemName

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
                'requesterSystem': self.consumer_system.no_auth,
                'requestedService': requested_service,
                'orchestrationFlags': orchestration_flags,
                'preferredProviders': {},
                'requestedQoS': {},
                'commands': {}
                }
        return service_request_form

    def consume(self):
        pass

if __name__ == '__main__':
    consumer = ServiceConsumer()
    a = consumer.system_name
    print(a)

    
