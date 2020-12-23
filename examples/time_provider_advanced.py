import datetime
from arrowhead_client.client import ProviderSystem
from flask import request
#from source.service_provider import ServiceProvider

class TimeProvider(ProviderSystem):
    def __init__(self, *args, **kwargs):
       ProviderSystem.__init__(self, *args, **kwargs)
       self.format = '%H:%M:%S'

    '''
    def setup_services(self):
        @self.add_service('time', '/time', 'HTTP-SECURITY_SECURE-JSON')
        def get_time():
            return datetime.datetime.now().strftime(self.format)
    
        @self.add_service('format', '/time/format', 'HTTP-SECURITY_SECURE-JSON', ['POST'])
        def change_format():
            data = request.data
    
            self.format = data.decode()
    
            return data
    '''

if __name__ == '__main__':
    # Create provider
    time_provider = TimeProvider.from_properties('examples/time_provider.properties')

    # Register services
    @time_provider.add_provided_service('time', '/time', 'HTTP-SECURITY_SECURE-JSON')
    def get_time():
        return datetime.datetime.now().strftime(time_provider.format)

    @time_provider.add_provided_service('format', '/time/format', 'HTTP-SECURITY_SECURE-JSON', ['POST'])
    def change_format():
        data = request.data

        time_provider.format = data.decode()

        return data

    # Run provider until shutdown
    time_provider.run_forever()
