from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service, ServiceInterface
from arrowhead_client.rules import OrchestrationRule, OrchestrationRuleContainer

provider_system = ArrowheadSystem.make('test', '127.0.0.1', 1337, '')
consumed_service = Service(
        'test',
        'test',
        ServiceInterface('HTTP', 'SECURE', 'JSON'),
        metadata={'dummy': 'data'},
)
method = 'GET'
authorization_token = 'token.token.token'

def test_orchestration_rule():
    rule = OrchestrationRule(
            consumed_service,
            provider_system,
            method,
            authorization_token
    )

    assert rule.service_definition == consumed_service.service_definition
    assert rule.protocol == consumed_service.interface.protocol
    assert rule.secure == consumed_service.interface.secure
    assert rule.payload_type == consumed_service.interface.payload
    assert rule.access_policy == consumed_service.access_policy
    assert rule.metadata == consumed_service.metadata
    assert rule.version == consumed_service.version
    assert rule.system_name == provider_system.system_name
    assert rule.endpoint == f'{provider_system.authority}/{consumed_service.service_uri}'
    assert rule.authentication_info == provider_system.authentication_info
    assert rule.method == method
    assert rule.authorization_token == authorization_token


def test_orchestration_rule_container_rule_input():
    rule_container = OrchestrationRuleContainer()

    rule = OrchestrationRule(
            consumed_service,
            provider_system,
            method,
            authorization_token
    )

    rule_container['first'] = rule
    rule_container.store(rule)

    assert rule_container['first'].service_definition == consumed_service.service_definition
    assert rule_container['test'].service_definition == consumed_service.service_definition

    del rule_container['first']
    assert rule_container.get('first') == None

    assert len(rule_container) == 1

    for key in rule_container:
        a = key


