"""
Async consumer example app
"""
import asyncio

from arrowhead_client.client.implementations import AsyncClient

consumer = AsyncClient.create(
        system_name='quickstart-consumer',
        address='127.0.0.1',
        port=7656,
        keyfile='certificates/crypto/quickstart-consumer.key',
        certfile='certificates/crypto/quickstart-consumer.crt',
        cafile='certificates/crypto/sysop.ca',
)


async def main(consumer):
    async with consumer:
        await consumer.add_orchestration_rule('hello-arrowhead', 'GET')
        await consumer.add_orchestration_rule('echo', 'PUT')

        aws = [
            consumer.consume_service('hello-arrowhead'),
            consumer.consume_service('echo', json={'msg': 'echo'})
        ]

        for i, aw in enumerate(asyncio.as_completed(aws)):
            print(i)
            print(await aw)

        await consumer.add_orchestration_rule('websocket_test', '*')

        connection = await consumer.connect('websocket_test')

        async with connection:
            while not connection.closed():
                await connection.send({'Q': 'Are WebSockets supported?'})
                print(await connection.receive())
            await connection.close()


async def print_response(consumer, service_definition, **kwargs):
    resp = await consumer.consume_service(service_definition, **kwargs)
    print(resp.read_json().get('msg'))


if __name__ == '__main__':
    asyncio.run(main(consumer))
