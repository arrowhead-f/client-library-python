"""
HttpProvider example app
"""
import arrowhead_client.api as ar

provider_app = ar.ArrowheadHttpClient(
        system_name='example-provider',
        address='127.0.0.1',
        port=7655,
        #keyfile='/home/jacnil/my-ah-cloud/certificates/crypto/example-provider.key',
        #certfile='/home/jacnil/my-ah-cloud/certificates/crypto/example-provider.crt'
        #keyfile='certificates/example-provider.key',
        #certfile='certificates/example-provider.crt',
)


@provider_app.provided_service(
        'hello-arrowhead',
        'hello',
        'HTTP-INSECURE-JSON',
        'GET', )
def hello_arrowhead(request):
    return {"msg": "Hello, Arrowhead!"}

if __name__ == '__main__':
    provider_app.run_forever()
