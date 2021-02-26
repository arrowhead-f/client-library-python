import arrowhead_client.api as ar

def test_provided_service():
    class CustomClient(ar.ArrowheadHttpClientSync):
        def __init__(self, *args, format='', **kwargs):
            super().__init__(*args, **kwargs)
            self.format = format

        @ar.provided_service(
                service_definition='hello-arrowhead',
                service_uri='hello',
                protocol='HTTP',
                method='GET',
                payload_format='JSON',
                access_policy='NOT_SECURE',
        )
        def service_function(self, request):
            return {'fmt': self.format}

    test_client = CustomClient('custom_client', '127.0.0.1', 1337, format='1Ab')

    test_client.setup()

    rule = list(test_client.registration_rules)[0]

    assert rule.service_definition == 'hello-arrowhead'
