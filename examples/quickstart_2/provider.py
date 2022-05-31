from pydantic import BaseModel

from arrowhead_client.client import AsyncClient, provided_service
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


class ProviderClient(AsyncClient):
    def __init__(self, state=0, **kwargs):
        super().__init__(**kwargs)
        self.state = state

    @provided_service(
            service_definition="counter",
            service_uri="counter",
            protocol="HTTP",
            method="GET",
            payload_format="JSON",
            access_policy="CERTIFICATE",
    )
    async def counter(self, req: Request):
        self.state = self.state + 1
        return {"counter": self.state}

    @provided_service(
            service_definition="set-state",
            service_uri="set",
            protocol="HTTP",
            method="PUT",
            payload_format="JSON",
            access_policy="CERTIFICATE",
    )
    async def set_state(self, req: Request[StateSetter]):
        self.state = req.data.state_update
        return None

if __name__ == "__main__":
    provider = ProviderClient.create(
            system_name="provider",
            address="172.16.1.1",
            port=6000,
            config=config,
            keyfile="/home/jacnil/.pyrrowhead/local-clouds/quickstart/tutorial/certs/crypto/provider-000.key",
            certfile="/home/jacnil/.pyrrowhead/local-clouds/quickstart/tutorial/certs/crypto/provider-000.crt",
            cafile="/home/jacnil/.pyrrowhead/local-clouds/quickstart/tutorial/certs/crypto/sysop.ca",
    )

    provider.run_forever()