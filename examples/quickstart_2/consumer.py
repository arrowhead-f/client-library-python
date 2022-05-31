import asyncio

from pydantic import BaseModel

from arrowhead_client.client import AsyncClient
from arrowhead_client.request import Request
from arrowhead_client.constants import CoreSystem


config = {
    'service_registry': {
        'system_name': CoreSystem.SERVICE_REGISTRY,
        'address': "172.16.1.3",
        'port': 8443,
    },
    'orchestrator': {
        'system_name': CoreSystem.ORCHESTRATOR,
        'address': "172.16.1.4",
        'port': 8441,
    },
    'authorization': {
        'system_name': CoreSystem.AUTHORIZATION,
        'address': "172.16.1.5",
        'port': 8445,
    },
}


class StateSetter(BaseModel):
    state_update: int

async def main(consumer: AsyncClient):
    async with consumer:
        await consumer.add_orchestration_rule('counter', 'GET')
        await consumer.add_orchestration_rule('set', 'PUT', data_model=StateSetter)

        a = (await consumer.consume_service('counter'))
        print(a)

if __name__ == "__main__":
    consumer = AsyncClient.create(
            system_name="consumer",
            address="172.16.1.1",
            port=6001,
            config=config,
            keyfile="/home/jacnil/.pyrrowhead/local-clouds/quickstart/tutorial/certs/crypto/consumer-000.key",
            certfile="/home/jacnil/.pyrrowhead/local-clouds/quickstart/tutorial/certs/crypto/consumer-000.crt",
            cafile="/home/jacnil/.pyrrowhead/local-clouds/quickstart/tutorial/certs/crypto/sysop.ca",
    )

    asyncio.run(main(consumer))

