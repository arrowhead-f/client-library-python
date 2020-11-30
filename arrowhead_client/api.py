"""
Arrowhead Client API module
===========================

This module contains the public api of the :code:`arrowhead_client` module.
"""
from arrowhead_client.configuration import config # noqa: F401
from arrowhead_client.client import ArrowheadClient
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.implementations.httpconsumer import HttpConsumer
from arrowhead_client.implementations.httpprovider import HttpProvider
from arrowhead_client.service import Service  # noqa: F401
from arrowhead_client.logs import get_logger



class ArrowheadHttpClient(ArrowheadClient):
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
                 keyfile: str = '',
                 certfile: str = ''):
        logger = get_logger(system_name, 'debug')
        system = ArrowheadSystem(system_name, address, port)
        super().__init__(
                system,
                HttpConsumer(),
                HttpProvider(system, keyfile, certfile),
                logger,
                keyfile=keyfile,
                certfile=certfile
        )
        self._logger.info(f'{self.__class__.__name__} initialized at {self.system.address}:{self.system.port}')
        # TODO: This line is a hack and needs to be fixed
