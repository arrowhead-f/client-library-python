from source.arrowhead_system import ArrowheadSystem
from source.service_provider import ServiceProvider
import datetime

def current_time():
    return str(datetime.datetime.now().strftime("%H:%M:%S"))

if __name__ == '__main__':
    time_system = ArrowheadSystem('Time', '127.0.0.1', '1337')
    time_consumer = ArrowheadSystem('time_consumer', '127.0.0.1', '1338')
    time_provider = ServiceProvider('Time', service_uri='/Time', provider_system=time_system, consumer_system=time_consumer)
    time_provider.add_route('/current_time', current_time)
    time_provider.run(auth=False)
