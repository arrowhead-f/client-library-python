from source.arrowhead_system import ConsumerSystem

time_consumer = ConsumerSystem('time_consumer',
                                  'localhost',
                                  '1338',
                                  '',
                                  '127.0.0.1',
                                  '8443',
                                  'certificates/time_consumer.key',
                                  'certificates/time_consumer.crt')
time_consumer.add_orchestration_rule('get_time', 'GET', 'time')

if __name__ == '__main__':
    time = time_consumer.consume('get_time')

    print(time)
