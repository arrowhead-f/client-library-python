from typing import Dict
import arrowhead_client.api as ar

time_provider = ar.ArrowheadHttpClient('time_provider',
                               'localhost',
                               1337,
                               '',
                               keyfile='certificates/time_provider.key',
                               certfile='certificates/time_provider.crt')

what_to_hello = 'Arrowhead'

@time_provider.provided_service('echo', 'echo', 'HTTP-SECURITY_SECURE-JSON', 'GET', hello_what=what_to_hello)
def echo(request, hello_what) -> Dict[str, str]:
    return {'msg': f'Hello {hello_what}'}


@time_provider.provided_service('hej', 'hej', 'HTTP-SECURITY_SECURE-JSON', 'POST')
def post(request) -> Dict[str, str]:
    print(request.json)
    what_to_hello = request.json['what_to_hello']
    return {'response': 'OK'}


@time_provider.provided_service('decorator', 'decorator', 'HTTP-SECURITY_SECURE-JSON', 'GET')
def decorator(request) -> Dict[str, str]:
    return {'Decorator': 'Success'}


if __name__ == '__main__':
    time_provider.run_forever()
