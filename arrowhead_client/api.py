from arrowhead_client.configuration import config
from arrowhead_client.application import ArrowheadApplication
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.consumer import Consumer
from arrowhead_client.provider import Provider
from arrowhead_client.logs import get_logger



class ArrowheadHttpApplication(ArrowheadApplication):
    def __init__(self,
                 system_name: str,
                 address: str,
                 port: int,
                 authentication_info: str = '',
                 keyfile: str = '',
                 certfile: str = ''):
        super().__init__(
                ArrowheadSystem(system_name, address, port, authentication_info),
                Consumer(keyfile, certfile),
                Provider(),
                get_logger(system_name, 'debug'),
                config,
                keyfile=keyfile,
                certfile=certfile
        )
        self._logger.info(f'{self.__class__.__name__} initialized at {self.system.address}:{self.system.port}')
        #TODO: This line is a hack and needs to be fixed
