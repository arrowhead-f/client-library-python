"""
Async provider example app
"""
from typing import Dict

from fastapi import WebSocket
from pydantic import BaseModel

from arrowhead_client.client import provided_service
from arrowhead_client.request import Request
from arrowhead_client.client.implementations import AsyncClient


class TestClient(AsyncClient):
    def __init__(self, *args, format: str = 'A', **kwargs):
        super().__init__(*args, **kwargs)
        self.format = format

    @provided_service(
            service_definition='hello-arrowhead',
            service_uri='hello',
            protocol='HTTP',
            method='GET',
            payload_format='JSON',
            access_policy='CERTIFICATE', )
    def hello(self, request: Request):
        self.format = 'C'
        return {'msg': self.format}


provider = TestClient.create(
        system_name='quickstart-provider',
        address='127.0.0.1',
        port=7655,
        keyfile='certificates/crypto/quickstart-provider.key',
        certfile='certificates/crypto/quickstart-provider.crt',
        cafile='certificates/crypto/sysop.ca',
        format='B'
)

'''
@provider.provided_service(
        service_definition='hello-arrowhead',
        service_uri='hello',
        protocol='HTTP',
        method='GET',
        payload_format='JSON',
        access_policy='CERTIFICATE', )
async def hello_arrowhead(request: Dict = None):
    return {"msg": "Hello, Arrowhead!"}
'''

class Test(BaseModel):
    a: int
    b: str

@provider.provided_service(
        service_definition='echo',
        service_uri='echo',
        protocol='HTTP',
        method='PUT',
        payload_format='JSON',
        access_policy='CERTIFICATE',
        data_model=Test,)
async def echo(request: Request[Test]):
    body = request

    return body


@provider.provided_service(
        service_definition='websocket_test',
        service_uri='ws_test',
        protocol='WS',
        method='',
        payload_format='JSON',
        access_policy='CERTIFICATE',
)
async def ws_test(websocket: WebSocket):
    await websocket.accept()
    for _ in range(3):
        data = await websocket.receive_json()
        await websocket.send_json({data['Q']: 'Yes'})
    await websocket.close()


if __name__ == '__main__':
    print(provider.__arrowhead_consumers__)
    provider.run_forever()
