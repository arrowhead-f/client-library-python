import datetime
from source.arrowhead_system import ProviderSystem
from source.provider import provided_service
from flask import request
#from source.service_provider import ServiceProvider

class TimeProvider(ProviderSystem):
    def __init__(self, *args, **kwargs):
       ProviderSystem.__init__(self, *args, **kwargs)
       self.format = '%H:%M:%S'

    def setup_services(self):
        @self.add_service('time', '/time', 'HTTP-SECURE-JSON')
        def get_time():
            return datetime.datetime.now().strftime(self.format)

        @self.add_service('format', '/time/format', 'HTTP-SECURE-JSON', ['POST'])
        def change_format():
            data = request.data

            print(data)

            self.format = data.decode()

            return True


if __name__ == '__main__':
    '''
    time_provider = TimeProvider('time_provider',
            'localhost',
            '1337',
            '',
            '127.0.0.1',
            '8443',
            'certificates/time_provider.key',
            'certificates/time_provider.crt')
    '''
    time_provider = TimeProvider.from_properties('examples/time_provider.properties')
    #time_provider.setup_services()
    time_provider.run_forever()
    print(time_provider.services)
