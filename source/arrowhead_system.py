import requests
import configparser
from source.provider import BaseProvider
from source.consumer import BaseConsumer

def parse_service_query_response(service_query_response, num_responses=1):
    service_query_data = service_query_response.json()['serviceQueryData']

    if not service_query_data:
        return []
    if num_responses == 1:
        return service_query_data[0]
    if num_responses > 1:
        return service_query_data[0:num_responses]
    else:
        raise ValueError("Number of requested responses must be larger than 0")


class BaseArrowheadSystem():
    '''
    Arrowhead System class.
    :param system_name: Name of the system
    :type system_name: str
    :param address: IP-address of the system (IPv4)
    :type address: str
    :param port: Port of the system
    :type port: str
    :param authentication_info: Authentication info for token security, not implented yet
    :type authentication_info: str
    :param sr_address: Local cloud service registry address
    :type sr_address: str
    :param sr_port: Local cloud service registry port
    :type sr_port: str
    :param keyfile: Location of tls keyfile
    :type keyfile: str
    :param certfile: Location of tls certfile
    :type certfile: str
    '''

    def __init__(self,
                 system_name,
                 address,
                 port,
                 authentication_info,
                 sr_address,
                 sr_port,
                 keyfile,
                 certfile):
        self.system_name = system_name
        self.address = address
        self.port = port
        self.authentication_info = authentication_info
        self.sr_address = sr_address
        self.sr_port = sr_port
        self.keyfile = keyfile
        self.certfile = certfile
        self.orch_address, self.orch_port = self._get_orch_url()

    @classmethod
    def from_properties(cls, properties_file):
        ''' Creates a BaseArrowheadSystem from a descriptor file '''

        # Parse configuration file
        config = configparser.ConfigParser()
        with open(properties_file, 'r') as properties:
            config.read_file(properties)
        config = dict(config._sections['SYSTEM'])

        # Create class instance
        system = cls(**config)

        return system

    @property
    def sr_url(self):
        '''
        Creates the service registry url given the address and port.

        :returns: Service registry url
        :rtype: str
        '''

        return f'{self.sr_address}:{self.sr_port}/serviceregistry'

    @property
    def orch_url(self):
        '''
        Creates the orchestrator url given the address and port.

        :returns: Orchestrator url
        :rtype: str
        '''

        return f'{self.orch_address}:{self.orch_port}/orchestrator'

    @property
    def system_json(self):
        '''
        Creates a dictionary of the BaseArrowheadSystem to be used in various forms.

        :returns: Representation of BaseArrowheadSystem
        :rtype: dict
        '''

        return {
            "systemName": self.system_name,
            "address": self.address,
            "port": int(self.port),
            "authenticationInfo": self.authentication_info
            }

    def _verify_sr(self):
        '''
        Verifies that the connection to the service registry is established.

        :returns: Verification of connection
        :rtype: bool
        :raises: :class:`RuntimeError`: Connection not established
        '''

        response = requests.get(f'https://{self.sr_url}/echo',
                                cert=(self.certfile, self.keyfile),
                                verify=False)
        if response.status_code >= 200 and response.status_code < 300:
            return True
        else:
            raise RuntimeError(f'Service registry error response <{r.status_code}>')

    def _query_sr(self,
                 service_definition_requirement,
                 interface_requirements,
                 security_requirements):
        '''
        Queries the service registry for a service

        :param service_definition_requirement: Requested service definition
        :type service_definition_requirement: str
        :param interface_requirements: Requested service interfaces
        :type interface_requirements: str
        :param security_requirements: Requested service security
        :type security_requirements: str

        :returns: service query response
        :rtype: dict
        '''

        service_query_form = {
            "serviceDefinitionRequirement": service_definition_requirement,
            "interfaceRequirements": [interface_requirements.upper()],
            "securityRequirements": [security_requirements.upper()],
            "metadataRequirements": None,
            "versionRequirement": None,
            "maxVersionRequirement": None,
            "minVersionRequirement": None,
            "pingProviders": True
            }

        service_query_response = requests.post(f'https://{self.sr_url}/query',
                                               cert=(self.certfile, self.keyfile),
                                               verify=False,
                                               json=service_query_form)

        return service_query_response


    def _get_orch_url(self):
        '''
        Request the orchestration service from the service registry

        :returns: Orchestrator address and port
        :rtype: tuple
        '''

        # Verify that sr is up and running
        self._verify_sr()

        service_query_response = self._query_sr('orchestration-service',
                                               'HTTP-SECURE-JSON',
                                               'CERTIFICATE')

        orchestrator_data = parse_service_query_response(service_query_response, 1)

        orch_address = orchestrator_data['provider']['address']
        # If the orchestrator address is 'orchestrator', assume that the orchestrator is found
        # On the same address as the service registry
        if orch_address == 'orchestrator':
            orch_address = self.sr_address
        orch_port = orchestrator_data['provider']['port']

        return orch_address, orch_port

class ProviderSystem(BaseProvider, BaseArrowheadSystem):
    def __init__(self, *args, **kwargs):
        BaseArrowheadSystem.__init__(self, *args, **kwargs)
        BaseProvider.__init__(self)

class ConsumerSystem(BaseConsumer, BaseArrowheadSystem):
    def __init__(self, *args, **kwargs):
        BaseArrowheadSystem.__init__(self, *args, **kwargs)
        BaseConsumer.__init__(self)

if __name__ == '__main__':
    test_system = ProviderSystem('time_provider',
                                      'localhost',
                                      '1337',
                                      '',
                                      '127.0.0.1',
                                      '8443',
                                      'certificates/time_provider.key',
                                      'certificates/time_provider.crt')

    from time import sleep
    test_system.run_forever()
        
