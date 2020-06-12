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
)

consumer_app.add_consumed_service('hello-arrowhead', 'GET')

if __name__ == '__main__':
    response = consumer_app.consume_service('hello-arrowhead')
    message = consumer_app.consumer.extract_payload(response, 'json')

    print(message['msg'])