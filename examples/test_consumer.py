from pprint import pprint
from source.arrowhead_system import ConsumerSystem

if __name__ == '__main__':
    consumer_test = ConsumerSystem('consumer_test',
                                      'localhost',
                                      '1338',
                                      '',
                                      '127.0.0.1',
                                      '8443',
                                      'certificates/consumer_test.key',
                                      'certificates/consumer_test.crt')
    consumer_test.add_orchestration_rule('read_echo', 'GET', 'echo')
    pprint(consumer_test.rule_dictionary)
    response = consumer_test.consume('read_echo')
    print(response.text)
