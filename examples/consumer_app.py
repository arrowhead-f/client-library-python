"""
HttpConsumer example app
"""
import arrowhead_client.api as ar

consumer_app = ar.ArrowheadHttpClient(
        system_name='example-consumer',
        address='127.0.0.1',
        port=7656,
        keyfile='certificates/example-consumer.key',
        certfile='certificates/example-consumer.crt',
        cafile='certificates/sysop.ca',
)


if __name__ == '__main__':
    consumer_app.setup()

    consumer_app.add_orchestration_rule('hello-arrowhead', 'GET', 'TOKEN')
    response = consumer_app.consume_service('hello-arrowhead')
    print(response.read_json()['msg'])

    consumer_app.add_orchestration_rule('echo', 'PUT', 'CERTIFICATE')
    echo_response = consumer_app.consume_service('echo', json={'msg': 'ECHO'})
    print(echo_response.read_json()['msg'])
