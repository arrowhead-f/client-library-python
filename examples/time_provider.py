from source.arrowhead_system import ArrowheadSystem
from source.service_provider import ServiceProvider
import datetime

time_format = "%H:%M:%S"
def current_time():
    return str(datetime.datetime.now().strftime(time_format))

if __name__ == '__main__':
    service_registry = ArrowheadSystem('Service registry', '127.0.0.1', '8443')
    time_system = ArrowheadSystem('Time', '127.0.0.1', '1337')
    time_provider = ServiceProvider('Time', service_uri='/Time', provider_system=time_system, service_registry=service_registry)
    time_provider.add_route('/current_time', current_time)
    time_provider.run(auth=False)
