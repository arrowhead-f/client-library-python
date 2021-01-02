"""
HttpProvider example app
"""
import arrowhead_client.api as ar

provider = ar.ArrowheadHttpClient(
        system_name='quickstart-provider',
        address='127.0.0.1',
        port=7655,
        keyfile='certificates/crypto/quickstart-provider.key',
        certfile='certificates/crypto/quickstart-provider.crt',
        cafile='certificates/crypto/sysop.ca',
)


@provider.provided_service(
        service_definition='hello-arrowhead',
        service_uri='hello',
        protocol='HTTP',
        method='GET',
        payload_format='JSON',
        access_policy='TOKEN', )
def hello_arrowhead(request):
    return {"msg": "Hello, Arrowhead!"}


@provider.provided_service(
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
    provider.run_forever()
