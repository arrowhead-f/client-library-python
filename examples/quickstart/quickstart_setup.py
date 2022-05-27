import subprocess
import requests
import time
from typing import List

from arrowhead_client.dto import DTOMixin
from arrowhead_client.rules import OrchestrationRule
from arrowhead_client.service import ServiceInterface
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service
from arrowhead_client.client.core_system_defaults import default_config
from arrowhead_client.forms import ServiceRegistrationForm
from arrowhead_client.client.implementations import SyncClient

subprocess.run(['docker-compose', 'down'])
subprocess.run(['docker', 'volume', 'rm', 'mysql.quickstart'])
subprocess.run(['docker', 'volume', 'create', '--name', 'mysql.quickstart'])
subprocess.run(['docker-compose', 'up', '-d'])

with requests.Session() as session:
    session.verify = 'certificates/crypto/sysop.ca'
    session.cert = ('certificates/crypto/sysop.crt', 'certificates/crypto/sysop.key')
    is_online = [False, False, False, False]
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
            #if not is_online[3]:
            #    session.get('https://127.0.0.1:8455/eventhandler/echo')
            #    is_online[3] = True
            #    print('Event Handler is online')
        except Exception:
            time.sleep(2)
        else:
            print('All core systems are online\n')
            break

setup_client = SyncClient.create(
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
                Service(
                        'mgmt_register_service',
                        'serviceregistry/mgmt',
                        ServiceInterface.from_str('HTTP-SECURE-JSON'),
                ),
                ArrowheadSystem(
                        **default_config['service_registry']
                ),
                'POST',
        )
)

setup_client.orchestration_rules.store(
        OrchestrationRule(
                Service(
                        'mgmt_get_systems',
                        'serviceregistry/mgmt/systems',
                        ServiceInterface('HTTP', 'SECURE', 'JSON'),
                ),
                ArrowheadSystem(
                        **default_config['service_registry']
                ),
                'GET',
        )
)

setup_client.orchestration_rules.store(
        OrchestrationRule(
                Service(
                        'mgmt_register_system',
                        'serviceregistry/mgmt/systems',
                        ServiceInterface('HTTP', 'SECURE', 'JSON'),
                ),
                ArrowheadSystem(
                        **default_config['service_registry']
                ),
                'POST',
        )
)

setup_client.orchestration_rules.store(
        OrchestrationRule(
                Service(
                        'mgmt_orchestration_store',
                        'orchestrator/mgmt/store',
                        ServiceInterface('HTTP', 'SECURE', 'JSON'),
                ),
                ArrowheadSystem(
                        **default_config['orchestrator']
                ),
                'POST',
        )
)

setup_client.orchestration_rules.store(
        OrchestrationRule(
                Service(
                        'mgmt_authorization_store',
                        'authorization/mgmt/intracloud',
                        ServiceInterface('HTTP', 'SECURE', 'JSON'),
                ),
                ArrowheadSystem(
                        **default_config['authorization']
                ),
                'POST',
        )
)

setup_client.setup()

consumer_system = ArrowheadSystem(
        system_name='quickstart-consumer',
        address='127.0.0.1',
        port=7656
)
provider_system = ArrowheadSystem(
        system_name='quickstart-provider',
        address='127.0.0.1',
        port=7655,
        authentication_info='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAhv0G6H'
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
    'consumer': (ArrowheadSystem.from_dto(consumer_data), consumer_data['id']),
    'provider': (ArrowheadSystem.from_dto(provider_data), provider_data['id']),
}

hello_form = ServiceRegistrationForm.make(
        Service(
                'hello-arrowhead',
                'hello',
                ServiceInterface.from_str('HTTP-SECURE-JSON'),
                'TOKEN',
        ),
        systems['provider'][0],
)
echo_form = ServiceRegistrationForm.make(
        Service(
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
    service_definition_name: str
    consumer_system_id: str
    provider_system: ArrowheadSystem
    service_interface_name: str
    priority: int = 1


hello_orch_form = OrchestrationMgmtStoreForm(
        service_definition_name='hello-arrowhead',
        consumer_system_id=systems['consumer'][1],
        provider_system=systems['provider'][0],
        service_interface_name='HTTP-SECURE-JSON',
)
echo_orch_form = OrchestrationMgmtStoreForm(
        service_definition_name='echo',
        consumer_system_id=systems['consumer'][1],
        provider_system=systems['provider'][0].dto(),
        service_interface_name='HTTP-SECURE-JSON',
)

res = setup_client.consume_service(
        'mgmt_orchestration_store',
        json=[hello_orch_form.dto(), echo_orch_form.dto()]
)


class AuthorizationIntracloudForm(DTOMixin):
    consumer_id: int
    provider_ids: List[int]
    interface_ids: List[int]
    service_definition_ids: List[int]


hello_auth_form = AuthorizationIntracloudForm(
        consumer_id=systems['consumer'][1],
        provider_ids=[systems['provider'][1]],
        interface_ids=[1],
        service_definition_ids=[hello_id],
)
echo_auth_form = AuthorizationIntracloudForm(
        consumer_id=systems['consumer'][1],
        provider_ids=[systems['provider'][1]],
        interface_ids=[1],
        service_definition_ids=[echo_id],
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
