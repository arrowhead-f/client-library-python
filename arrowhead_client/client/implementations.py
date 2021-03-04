from arrowhead_client.client import ArrowheadClientSync, ArrowheadClientAsync
from arrowhead_client.implementations.httpprovider import HttpProvider
from arrowhead_client.implementations.httpconsumer import HttpConsumer
from arrowhead_client.implementations.fastapi_provider import HttpProvider as AsyncHttpProvider
from arrowhead_client.implementations.aiohttp_consumer import AiohttpConsumer

class SyncClient(ArrowheadClientSync):
    __arrowhead_provider__ = HttpProvider
    __arrowhead_consumer__ = HttpConsumer

class AsyncClient(ArrowheadClientAsync):
    __arrowhead_provider__ = AsyncHttpProvider
    __arrowhead_consumer__ = AiohttpConsumer
