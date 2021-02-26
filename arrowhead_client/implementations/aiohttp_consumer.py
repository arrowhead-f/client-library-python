import ssl

import aiohttp

from arrowhead_client.abc import BaseConsumer
from arrowhead_client.response import Response
from arrowhead_client.rules import OrchestrationRule
from arrowhead_client.common import Constants


class AiohttpConsumer(BaseConsumer, protocol=Constants.PROTOCOL_HTTP):
    def __init__(
            self,
            keyfile: str,
            certfile: str,
            certificate_authority: str,
    ):
        if keyfile and certfile and certificate_authority:
            self.ssl_context = ssl.create_default_context(cafile=certificate_authority)
            self.ssl_context.load_cert_chain(certfile, keyfile)
        else:
            self.ssl_context = ssl.create_default_context()

        self.http_session = aiohttp.ClientSession()

    async def consume_service(
            self,
            rule: OrchestrationRule,
            **kwargs,
    ) -> Response:
        headers = kwargs['headers']
        if rule.secure:
            auth_header = {'Authorization': f'Bearer {rule.authorization_token}'}
            headers = {**kwargs['headers'], **auth_header}

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


def http(secure: str) -> str:
    if secure == Constants.SECURITY_INSECURE:
        return 'http://'
    return 'https://'
