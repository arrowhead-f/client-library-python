"""
HttpConsumer example app
"""
import asyncio

import arrowhead_client.api as ar

consumer = ar.ArrowheadHttpClientAsync(
        system_name='quickstart-consumer',
        address='127.0.0.1',
        port=7656,
        keyfile='certificates/crypto/quickstart-consumer.key',
        certfile='certificates/crypto/quickstart-consumer.crt',
        cafile='certificates/crypto/sysop.ca',
)

async def main():
    consumer.setup()

    consumer.add_orchestration_rule('hello-arrowhead', 'GET')
    response = await consumer.consume_service('hello-arrowhead')
    print(response.read_json()['msg'])

    consumer.add_orchestration_rule('echo', 'PUT')
    echo_response = await consumer.consume_service('echo', json={'msg': 'ECHO'})
    print(echo_response.read_json()['msg'])

if __name__ == '__main__':
    asyncio.run(main())