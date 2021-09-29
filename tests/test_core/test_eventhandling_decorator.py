from arrowhead_client.client.implementations import SyncClient
from arrowhead_client.client import subscribed_event

def test_subscribed_event_insecure_with_decorator():
    class CustomClient(SyncClient):
        def __init__(self, *args, format='', **kwargs):
            super().__init__(*args, **kwargs)
            self.format = format

        @subscribed_event(
                event_type='test_event',
                metadata={'meta': 'data'}
        )
        def on_test_event(self, request):
            pass

    test_client = CustomClient.create(
            'custom_client', '127.0.0.1', 1337, format='1Ab')

    test_client.setup()

    rule = list(test_client.event_subscription_rules.values())[0]

    assert 'on_test_event' not in SyncClient.__arrowhead_subscribed_events__
    assert rule.event_type == 'test_event'
    assert rule.metadata == {'meta': 'data'}
    assert rule.subscriber_system == test_client.system
    assert rule.notify_uri.split('/')[-1] == str(rule.uuid)


def test_subscribed_event_insecure_with_method():
    class CustomClient(SyncClient):
        def __init__(self, *args, format='', **kwargs):
            super().__init__(*args, **kwargs)
            self.format = format


    test_client = CustomClient.create(
            'custom_client', '127.0.0.1', 1337, format='1Ab')

    @test_client.subscribed_event(
            event_type='test_event',
            metadata={'meta': 'data'}
    )
    def on_test_event(request):
        pass

    test_client.setup()

    rule = list(test_client.event_subscription_rules.values())[0]

    assert rule.event_type == 'test_event'
    assert rule.metadata == {'meta': 'data'}
    assert rule.subscriber_system == test_client.system
    assert rule.notify_uri.split('/')[-1] == str(rule.uuid)
