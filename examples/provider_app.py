"""
HttpProvider example app
"""
import arrowhead_client.api as ar

ar.config['certificate authority'] = 'certificates/sysop.ca'
ar.config['app_name'] = __name__

provider_app = ar.ArrowheadHttpClient(
        system_name='example-provider',
        address='127.0.0.1',
        port=7655,
        keyfile='certificates/example-provider.key',
        certfile='certificates/example-provider.crt',
)


@provider_app.provided_service(
        service_definition='hello-arrowhead',
        service_uri='hello',
        interface='HTTP-SECURE-JSON',
        access_policy='TOKEN',
        method='GET', )
def hello_arrowhead(request):
    return {"msg": "Hello, Arrowhead!"}

if __name__ == '__main__':
    provider_app.run_forever()
