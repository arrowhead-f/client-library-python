from typing import Dict
import arrowhead_client.api as ar

time_provider = ar.ArrowheadSystem('time_provider',
                               'localhost',
                               1337,
                               '',
                               keyfile='certificates/time_provider.key',
                               certfile='certificates/time_provider.crt')


def echo(request) -> Dict[str, str]:
    return {'msg': 'Hello Arrowhead'}


def post(request) -> Dict[str, str]:
    print(request.json)
    return {'response': 'OK'}


@time_provider.provided_service('decorator', 'decorator', 'HTTP-SECURE-JSON', 'GET')
def decorator(request) -> Dict[str, str]:
    return {'Decorator': 'Success'}


if __name__ == '__main__':
    time_provider.add_provided_service(
            service_definition='echo',
            service_uri='echo',
            interface='HTTP-SECURE-JSON',
            http_method='GET',
            view_func=echo
    )

    time_provider.add_provided_service(
            service_definition='hej',
            service_uri='hej',
            interface='HTTP-SECURE-JSON',
            http_method='POST',
            view_func=post
    )

    time_provider.add_provided_service(
            'lambda',
            'lambda',
            'HTTP-SECURE-JSON',
            http_method='GET',
            view_func=lambda: {'lambda': True}
    )

    print(time_provider.certfile)
    time_provider.run_forever()
