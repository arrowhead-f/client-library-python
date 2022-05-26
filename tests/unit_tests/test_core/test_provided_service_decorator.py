from arrowhead_client.client.implementations import SyncClient
from arrowhead_client.client import provided_service


def test_provided_service_insecure_with_service_descriptor():
    class CustomClient(SyncClient):
        def __init__(self, *args, format='', **kwargs):
            super().__init__(*args, **kwargs)
            self.format = format

        @provided_service(
            service_definition='hello-arrowhead',
            service_uri='hello',
            protocol='HTTP',
            method='GET',
            payload_format='JSON',
            access_policy='NOT_SECURE',
        )
        def service_function(self, request):
            return {'fmt': self.format}

    test_client = CustomClient.create(
        'custom_client', '127.0.0.1', 1337, format='1Ab')

    test_client.setup()

    rule = list(test_client.registration_rules)[0]

    assert rule.service_definition == 'hello-arrowhead'
    assert rule.provided_service.interface.dto() == "HTTP-INSECURE-JSON"
    assert rule.provided_service.access_policy == "NOT_SECURE"


def test_provided_service_secure_with_service_descriptor():
    class CustomClient(SyncClient):
        def __init__(self, *args, format='', **kwargs):
            super().__init__(*args, **kwargs)
            self.format = format

        @provided_service(
            service_definition='hello-arrowhead',
            service_uri='hello',
            protocol='HTTP',
            method='GET',
            payload_format='JSON',
            access_policy='CERTIFICATE',
        )
        def service_function(self, request):
            return {'fmt': self.format}

    test_client = CustomClient.create(
        'custom_client', '127.0.0.1', 1337, format='1Ab')

    test_client.setup()

    rule = list(test_client.registration_rules)[0]

    assert rule.service_definition == 'hello-arrowhead'
    assert rule.provided_service.interface.dto() == "HTTP-SECURE-JSON"
    assert rule.provided_service.access_policy == "CERTIFICATE"


def test_provided_service_insecure_with_function_decorator():
    class CustomClient(SyncClient):
        def __init__(self, *args, format='', **kwargs):
            super().__init__(*args, **kwargs)
            self.format = format

    test_client = CustomClient.create(
        'custom_client', '127.0.0.1', 1337, format='1Ab')

    @test_client.provided_service(
        service_definition='hello-arrowhead',
        service_uri='hello',
        protocol='HTTP',
        method='GET',
        payload_format='JSON',
        access_policy='NOT_SECURE',
    )
    def service_function(request):
        return {'fmt': '1Ab'}

    rule = list(test_client.registration_rules)[0]

    assert rule.service_definition == 'hello-arrowhead'
    assert rule.provided_service.interface.dto() == "HTTP-INSECURE-JSON"
    assert rule.provided_service.access_policy == "NOT_SECURE"


def test_provided_service_secure_with_function_decorator():
    class CustomClient(SyncClient):
        def __init__(self, *args, format='', **kwargs):
            super().__init__(*args, **kwargs)
            self.format = format

    test_client = CustomClient.create(
        'custom_client', '127.0.0.1', 1337, format='1Ab')

    @test_client.provided_service(
        service_definition='hello-arrowhead',
        service_uri='hello',
        protocol='HTTP',
        method='GET',
        payload_format='JSON',
        access_policy='CERTIFICATE',
    )
    def service_function(request):
        return {'fmt': '1Ab'}

    rule = list(test_client.registration_rules)[0]

    assert rule.service_definition == 'hello-arrowhead'
    assert rule.provided_service.interface.dto() == "HTTP-SECURE-JSON"
    assert rule.provided_service.access_policy == "CERTIFICATE"
