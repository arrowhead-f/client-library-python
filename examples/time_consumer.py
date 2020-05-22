from arrowhead_client.system.consumer import ConsumerSystem

time_consumer = ConsumerSystem(
        system_name='consumer_test',
        address='localhost',
        port='1338',
        authentication_info='',
        keyfile='certificates/consumer_test.key',
        certfile='certificates/consumer_test.crt')

time_consumer.add_consumed_service('echo', 'GET')
time_consumer.add_consumed_service('hej', 'POST')

if __name__ == '__main__':
    echo_response = time_consumer.consume_service('echo')
    hej_response = time_consumer.consume_service('hej', json={'test': 5})
    print(echo_response)
    print(hej_response)
    print('Done')
    '''
    
    # Consume service provided by the 'get_time' rule
    time = time_consumer.consume('get_time')
    print(time.text)
    input()
    # Consume service provided by the 'change_format' rule
    time_consumer.consume('change_format', payload='%S:%M:%H')
    # Consume service provided by the 'get_time' rule
    time = time_consumer.consume('get_time')
    print(time.text)
    '''
