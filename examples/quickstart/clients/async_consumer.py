"""
HttpConsumer example app
"""
import asyncio

import arrowhead_client.api as ar


async def main():
    async with ar.ArrowheadHttpClientAsync(
                system_name='quickstart-consumer',
                address='127.0.0.1',
                port=7656,
                keyfile='certificates/crypto/quickstart-consumer.key',
                certfile='certificates/crypto/quickstart-consumer.crt',
                cafile='certificates/crypto/sysop.ca',
    ) as consumer:
        await consumer.add_orchestration_rule('hello-arrowhead', 'GET')
        await consumer.add_orchestration_rule('echo', 'PUT')

        for _ in range(3):
            hello_res, echo_res = await asyncio.gather(
                    consumer.consume_service('hello-arrowhead'),
                    consumer.consume_service('echo', json={'msg': 'ECHO'}),
            )
            print(hello_res.read_json()['msg'])
            print(echo_res.read_json()['msg'])

        await consumer.consumer.async_shutdown()

if __name__ == '__main__':
    asyncio.run(main())