"""
Arrowhead Client API module
===========================

This module contains the public api of the :code:`arrowhead_client` module.
"""
from typing import Dict
from arrowhead_client.client import (
    ArrowheadClientSync,
    provided_service,
    ArrowheadClientAsync,
)
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.implementations.httpconsumer import HttpConsumer
from arrowhead_client.implementations.httpprovider import HttpProvider
from arrowhead_client.implementations.fastapi_provider import HttpProvider as AsyncProvider
from arrowhead_client.implementations.aiohttp_consumer import AiohttpConsumer as AsyncConsumer
from arrowhead_client.service import Service  # noqa: F401
from arrowhead_client.logs import get_logger


class ArrowheadHttpClientSync(ArrowheadClientSync):
    """
    Arrowhead client using HTTP.

    Attributes:
        system_name: A string to assign the system name
        address: A string to assign the system address
        port: An int to assign the system port
        authentication_info: A string to assign the system authentication info
        keyfile: A string to assign the PEM keyfile
        certfile: A string to assign the PEM certfile
    """

    def __init__(self,
                 system_name: str,
                 address: str,
                 port: int,
                 config: Dict = None,
                 keyfile: str = '',
                 certfile: str = '',
                 cafile: str = ''):
        logger = get_logger(system_name, 'debug')
        system = ArrowheadSystem.with_certfile(
                system_name,
                address,
                port,
                certfile,
        )
        super().__init__(
                system,
                HttpConsumer(keyfile, certfile, cafile),
                HttpProvider(cafile),
                logger,
                config=config,
                keyfile=keyfile,
                certfile=certfile
        )
        self._logger.info(f'{self.__class__.__name__} initialized at {self.system.address}:{self.system.port}')


class ArrowheadHttpClientAsync(ArrowheadClientAsync):
    def __init__(self,
                 system_name: str,
                 address: str,
                 port: int,
                 config: Dict = None,
                 keyfile: str = '',
                 certfile: str = '',
                 cafile: str = ''):
        logger = get_logger(system_name, 'debug')
        system = ArrowheadSystem.with_certfile(
                system_name,
                address,
                port,
                certfile,
        )
        super().__init__(
                system,
                AsyncConsumer(keyfile, certfile, cafile),
                AsyncProvider(cafile),
                logger,
                config=config,
                keyfile=keyfile,
                certfile=certfile
        )
        self._logger.info(f'{self.__class__.__name__} initialized at {self.system.address}:{self.system.port}')
