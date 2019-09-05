from codelab_adapter_client import AdapterNode


class DemoNode(AdapterNode):
    def __init__(self):
        # super().__init__(name='TestExtension2',codelab_adapter_ip_address="192.168.31.148")
        super().__init__(name='demoNode')
        # self.set_subscriber_topic('eim')

def test_subscribed_topics():
    node = DemoNode()
    # node.subscriber
    assert node.subscribed_topics == set(node.subscriber_list)
    node.clean_up()
    # import IPython;IPython.embed()

