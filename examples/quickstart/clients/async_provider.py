"""
HttpProvider example app
"""
from typing import Dict, Optional
import asyncio

from fastapi import WebSocket, WebSocketDisconnect

import arrowhead_client.api as ar
from arrowhead_client.request import Request

provider = ar.ArrowheadHttpClientAsync(
        system_name='quickstart-provider',
        address='127.0.0.1',
        port=7655,
        keyfile='certificates/crypto/quickstart-provider.key',
        certfile='certificates/crypto/quickstart-provider.crt',
        cafile='certificates/crypto/sysop.ca',
)


@provider.provided_service(
        service_definition='hello-arrowhead',
        service_uri='hello',
        protocol='HTTP',
        method='GET',
        payload_format='JSON',
        access_policy='CERTIFICATE', )
async def hello_arrowhead(request: Dict = None):
    return {"msg": "Hello, Arrowhead!"}


@provider.provided_service(
        service_definition='echo',
        service_uri='echo',
        protocol='HTTP',
        method='PUT',
        payload_format='JSON',
        access_policy='CERTIFICATE', )
async def echo(request: Dict):
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
    provider.run_forever()
