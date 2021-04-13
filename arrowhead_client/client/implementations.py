from arrowhead_client.client.client_sync import ArrowheadClientSync
from arrowhead_client.client.client_async import ArrowheadClientAsync
from arrowhead_client.provider.implementations.httpprovider import FlaskProvider
from arrowhead_client.consumer.implementations.requests_consumer import RequestsConsumer
from arrowhead_client.provider.implementations.fastapi_provider import FastapiProvider as AsyncHttpProvider
from arrowhead_client.consumer.implementations.aiohttp_consumer import AiohttpConsumer


class SyncClient(ArrowheadClientSync):
    """
    Asynchronous ArrowheadClient implementation for HTTP and Websockets services.

    Example::

        from typing import Dict
        from arrowhead_client.client import SyncClient

        # Create an SyncClient in insecure mode
        example_client = SyncClient.create(
                system_name='example_client',
                address='127.0.0.1',
                port=5678,
        )

        # Add a service that responds with 'ECHO'
        @example_client.provided_service(
                service_definition='echo',
                service_uri='example/echo',
                protocol='HTTP',
                method='GET',
                payload_format='TEXT',
                access_policy='NOT_SECURE',
        )
        def echo(request):
            return "ECHO"

    """
    __arrowhead_provider__ = FlaskProvider
    __arrowhead_consumer__ = RequestsConsumer


class AsyncClient(ArrowheadClientAsync):
    """
    Asynchronous ArrowheadClient implementation for HTTP and Websockets services.

    Example::

        from typing import Dict
        from arrowhead_client.client import AsyncClient

        # Create an AsyncClient in insecure mode
        example_client = AsyncClient.create(
                system_name='example_client',
                address='127.0.0.1',
                port=5678,
        )

        # Add a service that responds with 'ECHO'
        @example_client.provided_service(
                service_definition='echo',
                service_uri='example/echo',
                protocol='HTTP',
                method='GET',
                payload_format='TEXT',
                access_policy='NOT_SECURE',
        )
        async def echo(input: Dict):
            return "ECHO"

    """
    __arrowhead_provider__ = AsyncHttpProvider
    __arrowhead_consumer__ = AiohttpConsumer
