from source.arrowhead_system import ArrowheadSystem
from source.service_consumer import ServiceConsumer
import requests

if __name__ == '__main__':
    service_registry = ArrowheadSystem('Service registry', '127.0.0.1', '8442')
    time_consumer = ServiceConsumer('time_consumer', '127.0.0.1', '1338', service_registry=service_registry)
    time = time_consumer.consume('Time', 'current_time', requests.get)
    print(time.text)

