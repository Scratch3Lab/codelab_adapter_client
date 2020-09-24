import time
from loguru import logger
from codelab_adapter_client import AdapterNode

class EimMonitorNode(AdapterNode):
    '''
    fork from https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/nodes_v3/node_eim_monitor.py
    '''

    NODE_ID = "eim"
    HELP_URL = "http://adapter.codelab.club/extension_guide/eim_monitor/"
    WEIGHT = 97
    DESCRIPTION = "响应一条eim消息"

    def __init__(self, monitor_func, **kwargs):
        super().__init__(**kwargs)
        self.monitor_func = monitor_func

    def extension_message_handle(self, topic, payload):
        content = payload["content"]
        # response = sys.modules["eim_monitor"].monitor(content, self.logger)
        payload["content"] = self.monitor_func(content)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        while self._running:
            time.sleep(0.1)


if __name__ == "__main__":
    def monitor(content):
        return content[::-1]
    try:
        node = EimMonitorNode(monitor)
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.