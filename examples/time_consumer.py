from pprint import pprint
from arrowhead_client.arrowhead_system import ConsumerSystem

time_consumer = ConsumerSystem('consumer_test',
                                  'localhost',
                                  '1338',
                                  '',
                                  '127.0.0.1',
                                  '8443',
                                  'certificates/consumer_test.key',
                                  'certificates/consumer_test.crt')

time_consumer.add_orchestration_rule('get_time', 'GET', 'time')
time_consumer.add_orchestration_rule('change_format', 'POST', 'format')

if __name__ == '__main__':
    time = time_consumer.consume('get_time')
    print(time.text)
    input()
    time_consumer.consume('change_format', payload='%S:%M:%H')
    time = time_consumer.consume('get_time')
    print(time.text)
