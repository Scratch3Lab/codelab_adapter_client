from codelab_adapter_client import AdapterNode


class TestNode:
    @classmethod
    def setup_class(cls):
        """
        https://www.jianshu.com/p/a57b5967f08b
        整个类只执行一次，如果是测试用例级别的则用setup_method
        """

        class DemoNode(AdapterNode):
            def __init__(self):
                # super().__init__(name='TestExtension2',codelab_adapter_ip_address="192.168.31.148")
                super().__init__(name='demoNode')
                # self.set_subscriber_topic('eim')

        cls.node = DemoNode()

    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        cls.node.clean_up()

    def test___str__(self):
        # print("ok")
        assert str(self.node) == "demoNode"
