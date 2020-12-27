"""
HttpProvider example app
"""
import arrowhead_client.api as ar

provider_app = ar.ArrowheadHttpClient(
        system_name='example-provider',
        address='127.0.0.1',
        port=7655,
        keyfile='certificates/example-provider.key',
        certfile='certificates/example-provider.crt',
        cafile='certificates/sysop.ca',
)


@provider_app.provided_service(
        service_definition='hello-arrowhead',
        service_uri='hello',
        protocol='HTTP',
        method='GET',
        payload_format='JSON',
        access_policy='TOKEN', )
def hello_arrowhead(request):
    return {"msg": "Hello, Arrowhead!"}

@provider_app.provided_service(
        service_definition='echo',
        service_uri='echo',
        protocol='HTTP',
        method='PUT',
        payload_format='JSON',
        access_policy='CERTIFICATE', )
def echo(request):
    body = request.read_json()

    return body

if __name__ == '__main__':
    provider_app.run_forever()
