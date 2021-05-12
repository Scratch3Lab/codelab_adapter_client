import time
import queue

from loguru import logger
from codelab_adapter_client.mqtt_node import MQTT_Node


class HelloCloudNode(MQTT_Node):
    '''
    在 cloud jupyterlab（jupyterhub） 里与Scratch通信
        以交互计算课程为测试场景
    '''

    def __init__(self, **kwargs):
        super().__init__(sub_topics=["eim/from_scratch"], **kwargs)
        self.message_queue = queue.Queue()
        self._latest_send_time = 0

    def on_message(self, client, userdata, msg):
        logger.debug(f"topic->{msg.topic} ;payload-> {msg.payload}")
        self.message_queue.put(msg.payload.decode()) # 来自 Scratch
        # import IPython;IPython.embed()
        # todo reply mqtt
        # logger.debug((client, userdata, msg))

    def _send_message(self, content):
        '''
        限制速率
        '''
        self.publish("eim/from_python", str(content))
        send_time = time.time()
        if send_time -  self._latest_send_time < 0.15:
            time.sleep(0.15)     
        self._latest_send_time = send_time

    def _receive_message(self, block=False):
        if block:
            return self.message_queue.get()
        else:
            try:
                return str(self.message_queue.get_nowait())
            except queue.Empty:
                time.sleep(0.01)
                return None


node = HelloCloudNode()

send_message = node._send_message
receive_message = node._receive_message