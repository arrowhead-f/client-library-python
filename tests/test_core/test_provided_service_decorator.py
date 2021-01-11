import arrowhead_client.api as ar

class CustomClient(ar.ArrowheadHttpClient):
    def __init__(self, *args, format='', **kwargs):
        super().__init__(*args, **kwargs)
        self.format = format

    @ar.provided_service(
            service_definition='hello-arrowhead',
            service_uri='hello',
            protocol='HTTP',
            method='GET',
            payload_format='JSON',
            access_policy='TOKEN',
    )
    def service_function(self):
        return {'fmt': self.format}

test_client = CustomClient('custom_client', '127.0.0.1', 1337, format='1Ab')

test_client.setup()
print(dir(test_client))
for rule in test_client.registration_rules:
    print(rule.service_definition)

