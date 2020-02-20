import datetime
from source.arrowhead_system import ProviderSystem
#from source.service_provider import ServiceProvider

time_provider = ProviderSystem('time_provider',
        'localhost',
        '1337',
        '',
        '127.0.0.1',
        '8443',
        'certificates/time_provider.key',
        'certificates/time_provider.crt')

@time_provider.add_service('time', '/time', 'HTTP-SECURE-JSON')
def get_time():
    return datetime.datetime.now().strftime('%H:%M:%S')


if __name__ == '__main__':
    time_provider.run_forever()
    print(time_provider.services)
    '''
    service_registry = ArrowheadSystem('Service registry', '127.0.0.1', '8443')
    time_system = ArrowheadSystem('Time', '127.0.0.1', '1337')
    time_provider = ServiceProvider('Time', service_uri='/Time', provider_system=time_system, service_registry=service_registry)
    time_provider.add_route('/current_time', current_time)
    time_provider.run(auth=False)
    '''
