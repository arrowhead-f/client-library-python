import ssl

import aiohttp

from arrowhead_client.consumer.base import BaseConsumer
from arrowhead_client.response import Response, ConnectionResponse
from arrowhead_client.rules import OrchestrationRule
from arrowhead_client import constants


class AiohttpConsumer(BaseConsumer, protocol=constants.Protocol.HTTP):
    """
    Asynchronous consumer based on AioHttp.
    """

    def __init__(
            self,
            keyfile: str,
            certfile: str,
            cafile: str,
    ):
        super().__init__(keyfile, certfile, cafile)
        if keyfile and certfile and cafile:
            self.ssl_context = ssl.create_default_context(cafile=cafile)
            self.ssl_context.load_cert_chain(certfile, keyfile)
        else:
            self.ssl_context = ssl.create_default_context()

        self.http_session: aiohttp.ClientSession

    async def async_startup(self):
        self.http_session = aiohttp.ClientSession()

    async def async_shutdown(self):
        await self.http_session.close()

    async def consume_service(  # type: ignore
            self,
            rule: OrchestrationRule,
            **kwargs,
    ) -> Response:
        headers = kwargs.get('headers', {})
        if rule.secure:
            auth_header = {'Authorization': f'Bearer {rule.authorization_token}'}
            headers = {**headers, **auth_header}

        async with self.http_session.request(
                rule.method,
                f'{http(rule.secure)}{rule.endpoint}',
                headers=headers,
                ssl=self.ssl_context,
                **kwargs,
        ) as resp:
            status_code = resp.status
            raw_response = await resp.read()

        return Response(raw_response, rule.payload_type, status_code)

    async def connect(
            self,
            rule: OrchestrationRule,
            **kwargs,
    ) -> "WebSocketResponse":
        headers = kwargs.get('headers', {})
        if rule.secure:
            auth_header = {'Authorization': f'Bearer {rule.authorization_token}'}
            headers = {**headers, **auth_header}

        connection = await self.http_session.ws_connect(
                f'{ws(rule.secure)}{rule.endpoint}',
                ssl=self.ssl_context,
                headers=headers,
                **kwargs,
        )

        return WebSocketResponse(connection, rule.payload_type)


class WebSocketResponse(ConnectionResponse):
    def __init__(
            self,
            connector: aiohttp.ClientWebSocketResponse,
            payload_type,
    ):
        super().__init__(connector)
        self.payload_type = payload_type

    async def send(self, data):
        if self.payload_type == constants.Payload.JSON:
            return await self._connector.send_json(data)
        elif self.payload_type == constants.Payload.TEXT:
            return await self._connector.send_str(data)
        else:
            return await self._connector.send_bytes(data)

    async def receive(self):
        # TODO: This try clause is a janky solution to fix an error that occurs when connection is closed
        # while a message is awaited that is not of the correct type. There is definetly a better solution
        # to this but it is unclear at the moment.
        try:
            if self.payload_type == constants.Payload.JSON:
                res = await self._connector.receive_json()
            elif self.payload_type == constants.Payload.TEXT:
                res = await self._connector.receive_str()
            else:
                res = await self._connector.receive_bytes()
        except TypeError as e:
            if str(e) == 'Received message 8:1000 is not str':
                return
            raise e
        else:
            return res

    async def close(self):
        return await self._connector.close()

    def closed(self):
        return self._connector.closed


def http(secure: str) -> str:
    if secure == constants.Security.INSECURE:
        return 'http://'
    return 'https://'


def ws(secure: str) -> str:
    if secure == constants.Security.INSECURE:
        return 'ws://'
    return 'wss://'
