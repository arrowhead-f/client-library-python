from arrowhead_client.api import ArrowheadHttpClient

time_consumer = ArrowheadHttpClient(
        system_name='consumer_test',
        address='localhost',
        port=1338,
        authentication_info='',
        keyfile='certificates/consumer_test.key',
        certfile='certificates/consumer_test.crt')

time_consumer.add_consumed_service('echo', method='GET')
time_consumer.add_consumed_service('hej', method='POST')

if __name__ == '__main__':
    echo_response = time_consumer.consume_service('echo')
    hej_response = time_consumer.consume_service('hej', json={'test': 5})
    print(echo_response)
    print(hej_response)
    print('Done')
    '''
    
    # Consume provided_service provided by the 'get_time' rule
    time = time_consumer.consume('get_time')
    print(time.text)
    input()
    # Consume provided_service provided by the 'change_format' rule
    time_consumer.consume('change_format', payload='%S:%M:%H')
    # Consume provided_service provided by the 'get_time' rule
    time = time_consumer.consume('get_time')
    print(time.text)
    '''
