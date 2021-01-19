import subprocess
import requests
import time

from arrowhead_client.dto import DTOMixin
from arrowhead_client.rules import OrchestrationRule
from arrowhead_client.service import ServiceInterface
from arrowhead_client.client.core_system_defaults import default_config
from arrowhead_client.client.core_service_forms import ServiceRegistrationForm
import arrowhead_client.api as ar

subprocess.run(['docker', 'volume', 'rm', 'mysql.quickstart'])
subprocess.run(['docker', 'volume', 'create', '--name', 'mysql.quickstart'])
subprocess.run(['docker-compose', 'up', '-d'])

with requests.Session() as session:
    session.verify = 'certificates/crypto/sysop.ca'
    session.cert = ('certificates/crypto/sysop.crt', 'certificates/crypto/sysop.key')
    is_online = [False, False, False]
    print('Waiting for core systems to get online (might take a few minutes...)')
    while True:
        try:
            if not is_online[0]:
                session.get('https://127.0.0.1:8443/serviceregistry/echo')
                is_online[0] = True
                print('Service Registry is online')
            if not is_online[1]:
                session.get('https://127.0.0.1:8441/orchestrator/echo')
                is_online[1] = True
                print('Orchestrator is online')
            if not is_online[2]:
                session.get('https://127.0.0.1:8445/authorization/echo')
                is_online[2] = True
                print('Authorization is online')
        except Exception as e:
            time.sleep(2)
        else:
            print('All core systems are online\n')
            break

setup_client = ar.ArrowheadHttpClient(
        system_name='sysop',
        address='127.0.0.1',
        port=1337,
        keyfile='certificates/crypto/sysop.key',
        certfile='certificates/crypto/sysop.crt',
        cafile='certificates/crypto/sysop.ca'
)

print('Setting up local cloud')

setup_client.orchestration_rules.store(
        OrchestrationRule(
                ar.Service(
                        'mgmt_register_service',
                        'serviceregistry/mgmt',
                        ServiceInterface.from_str('HTTP-SECURE-JSON'),
                ),
                ar.ArrowheadSystem(
                        **default_config['service_registry']
                ),
                'POST',
        )
)

setup_client.orchestration_rules.store(
        OrchestrationRule(
                ar.Service(
                        'mgmt_get_systems',
                        'serviceregistry/mgmt/systems',
                        ServiceInterface('HTTP', 'SECURE', 'JSON'),
                ),
                ar.ArrowheadSystem(
                        **default_config['service_registry']
                ),
                'GET',
        )
)

setup_client.orchestration_rules.store(
        OrchestrationRule(
                ar.Service(
                        'mgmt_register_system',
                        'serviceregistry/mgmt/systems',
                        ServiceInterface('HTTP', 'SECURE', 'JSON'),
                ),
                ar.ArrowheadSystem(
                        **default_config['service_registry']
                ),
                'POST',
        )
)

setup_client.orchestration_rules.store(
        OrchestrationRule(
                ar.Service(
                        'mgmt_orchestration_store',
                        'orchestrator/mgmt/store',
                        ServiceInterface('HTTP', 'SECURE', 'JSON'),
                ),
                ar.ArrowheadSystem(
                        **default_config['orchestrator']
                ),
                'POST',
        )
)

setup_client.orchestration_rules.store(
        OrchestrationRule(
                ar.Service(
                        'mgmt_authorization_store',
                        'authorization/mgmt/intracloud',
                        ServiceInterface('HTTP', 'SECURE', 'JSON'),
                ),
                ar.ArrowheadSystem(
                        **default_config['authorization']
                ),
                'POST',
        )
)

setup_client.setup()

consumer_system = ar.ArrowheadSystem(
        'quickstart-consumer',
        '127.0.0.1',
        7656
)
provider_system = ar.ArrowheadSystem(
        'quickstart-provider',
        '127.0.0.1',
        7655,
        'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAhv0G6H'
        'Cst8lQlAXuevgoZpozM6XKT7ihtrWGfrN4vYG+e0f1b2Q88glW'
        'G+VjrD++dnjSmoU4f/7CTSvwcDtjsW4UFHWJNIkHF8WvugPT7Q'
        '5HaWr80uO0P+JNfbMD9e2FzMLRt9SBrTUKIMSXV/pQSGWQNQg5'
        'QK0oAaeQT0RPgC8+XwKck0R33DCuh/I6gtPKlgGcOkabbbZucP'
        'oRY6ZldB5Tm11mlWagjUGOzX3c8e2nhb02CDWcq8DWZW8cCBru'
        'ODyicvk/Ocda3di4MtYkSdbsy6jbrQsTJnd5FXtAMAbeAnyY/S'
        'b485AyByya7KQTmPAXVqnDZi314enjwJAJswIDAQAB',
)

consumer_data = setup_client.consume_service(
        'mgmt_register_system', json=consumer_system.dto()
).read_json()
provider_data = setup_client.consume_service(
        'mgmt_register_system', json=provider_system.dto()
).read_json()

systems = {
    'consumer': (ar.ArrowheadSystem.from_dto(consumer_data), consumer_data['id']),
    'provider': (ar.ArrowheadSystem.from_dto(provider_data), provider_data['id']),
}

hello_form = ServiceRegistrationForm(
        ar.Service(
                'hello-arrowhead',
                'hello',
                ServiceInterface.from_str('HTTP-SECURE-JSON'),
                'TOKEN',
        ),
        systems['provider'][0],
)
echo_form = ServiceRegistrationForm(
        ar.Service(
                'echo',
                'echo',
                ServiceInterface.from_str('HTTP-SECURE-JSON'),
                'CERTIFICATE',
        ),
        systems['provider'][0],
)

hello_res = setup_client.consume_service(
        'mgmt_register_service',
        json=hello_form.dto(),
).read_json()
echo_res = setup_client.consume_service(
        'mgmt_register_service',
        json=echo_form.dto(),
).read_json()
hello_id = hello_res['serviceDefinition']['id']
echo_id = echo_res['serviceDefinition']['id']

class OrchestrationMgmtStoreForm(DTOMixin):
    def __init__(
            self,
            service_definition_name: str,
            consumer_system_id: str,
            provider_system_dto: str,
            service_interface_name: str,
            priority: int = 1
    ):
        self.service_definition_name = service_definition_name
        self.consumer_system_id = consumer_system_id
        self.provider_system = provider_system_dto
        self.service_interface_name = service_interface_name
        self.priority = priority

hello_orch_form = OrchestrationMgmtStoreForm(
        'hello-arrowhead',
        systems['consumer'][1],
        systems['provider'][0].dto(),
        'HTTP-SECURE-JSON',
)
echo_orch_form = OrchestrationMgmtStoreForm(
        'echo',
        systems['consumer'][1],
        systems['provider'][0].dto(),
        'HTTP-SECURE-JSON',
)

res = setup_client.consume_service(
        'mgmt_orchestration_store',
        json=[hello_orch_form.dto(), echo_orch_form.dto()]
)

class AuthorizationIntracloudForm(DTOMixin):
    def __init__(
            self,
            consumer_id: int,
            provider_ids,
            interface_ids,
            service_definition_ids,
    ):
        self.consumer_id = consumer_id
        self.provider_ids = provider_ids
        self.interface_ids = interface_ids
        self.service_definition_ids = service_definition_ids

hello_auth_form = AuthorizationIntracloudForm(
        systems['consumer'][1],
        [systems['provider'][1]],
        [1],
        [hello_id],
)
echo_auth_form = AuthorizationIntracloudForm(
        systems['consumer'][1],
        [systems['provider'][1]],
        [1],
        [echo_id],
)

setup_client.consume_service(
        'mgmt_authorization_store',
        json=hello_auth_form.dto()
)
setup_client.consume_service(
        'mgmt_authorization_store',
        json=echo_auth_form.dto()
)

print('Local cloud setup finished!')
