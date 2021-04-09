import time
import queue

from loguru import logger
from codelab_adapter_client import AdapterNode


class HelloNode(AdapterNode):
    '''
    为入门者准备(CodeLab 交互计算 课程)
    fork from https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/nodes_v3/node_eim_monitor.py
    '''

    NODE_ID = "eim"
    HELP_URL = "http://adapter.codelab.club/extension_guide/HelloNode/"
    WEIGHT = 97
    DESCRIPTION = "hello node"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message_queue = queue.Queue()

    def extension_message_handle(self, topic, payload):
        content = payload["content"]
        self.message_queue.put(content)
        # response = sys.modules["eim_monitor"].monitor(content, self.logger)
        if payload.get("message_type") == "nowait":
            return
        else:
            payload["content"] = "ok"
            message = {"payload": payload}
            self.publish(message)

    def _send_message(self, content):
        message = self.message_template()
        message["payload"]["content"] = str(content)
        self.publish(message)
        time.sleep(0.05)  # 避免过快发送消息 20/s
    
    def _receive_message(self):
        try:
            return str(self.message_queue.get_nowait())
        except queue.Empty:
            time.sleep(0.01)
            return None


node = HelloNode()
node.receive_loop_as_thread()
time.sleep(0.1)  # wait for connecting

send_message = node._send_message
receive_message = node._receive_message