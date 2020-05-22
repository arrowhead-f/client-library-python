from typing import Dict
from arrowhead_client.system.provider import ProviderSystem

time_provider = ProviderSystem('time_provider',
                               'localhost',
                               1337,
                               '',
                               keyfile='certificates/time_provider.key',
                               certfile='certificates/time_provider.crt')


def echo() -> Dict[str, str]:
    return {'msg': 'Hello Arrowhead'}


def post(request) -> Dict[str, str]:
    print(request.json)
    return {'response': 'OK'}


@time_provider.provided_service('decorator', 'decorator', 'HTTP-SECURE-JSON', 'GET')
def decorator() -> Dict[str, str]:
    return {'Decorator': 'Success'}


if __name__ == '__main__':
    time_provider.add_provided_service(
            service_definition='echo',
            service_uri='echo',
            interface='HTTP-SECURE-JSON',
            http_method='GET',
            provides=echo
    )

    time_provider.add_provided_service(
            service_definition='hej',
            service_uri='hej',
            interface='HTTP-SECURE-JSON',
            http_method='POST',
            provides=post
    )

    time_provider.add_provided_service(
            'lambda',
            'lambda',
            'HTTP-SECURE-JSON',
            'GET',
            provides=lambda: {'lambda': True}
    )

    time_provider.run_forever()
