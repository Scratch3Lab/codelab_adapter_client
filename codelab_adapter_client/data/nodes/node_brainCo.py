'''
发出eim信号，使用eim做实验，不写新积木， osc? 两个信号

内置依赖，打包，相对路径
'''
import time
import json
import sys
import random
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.thing import AdapterThing

'''
DEBUG = False
if DEBUG:
    sys.path.append('/Users/wuwenjie/mylab/codelabclub/lab/adapter_build_embedded/adapterapp/src')  # brainCoSdk
'''
from brainCoSdk.fusi_sdk import *

from codelab_adapter_client.config import settings
from loguru import logger
debug_log = str(settings.NODE_LOG_PATH / "brainCo.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class MyListener(FusiHeadbandListener):
    def __init__(self, headband, node_instance):
        self.headband = headband
        self.node_instance = node_instance

    def on_connection_change(self, connection_state):
        self.node_instance.logger.debug("Connection state changed:%s" % connection_state.name)
        if connection_state == ConnectionState.connected:
            self.headband.set_forehead_led_color((255, 0, 0))
            self.node_instance.logger.debug("Headband connected")
            self.node_instance.pub_notification("头环 已连接", type="SUCCESS")
        elif connection_state == ConnectionState.interrupted:
            self.node_instance.logger.debug("Headband connection interrupted")
            self.node_instance.pub_notification("头环 连接中断", type="ERROR")
        elif connection_state == ConnectionState.disconnected:
            self.node_instance.logger.debug("Headband disconnected")
            self.node_instance.pub_notification("头环 已断开", type="ERROR")

    def _send_to_adapter(self, content, message_type="setProperty"):
        message = self.node_instance.message_template()
        message["payload"]["content"] = content
        message["payload"]["message_type"] = message_type
        # property_notify属性的变化
        self.node_instance.publish(message)

    def on_attention(self, attention):
        self.node_instance.logger.debug("Attention: %.3f" % attention)
        self._send_to_adapter({"attention": attention})

    def on_meditation(self, meditation):
        self.node_instance.logger.debug("Meditation: %.3f" % meditation)
        self._send_to_adapter({"meditation": meditation})

    def on_signal_quality_warning(self):
        self.node_instance.logger.debug("Signal is noisy")

class ThingProxy(AdapterThing):
    def __init__(self, node_instance):
        super().__init__(thing_name="BrainCo",
                         node_instance=node_instance)
        self.thing = None
        self.devices = None
        self.current_devices = None

    def _on_found_devices(self, devices):
        self.devices = devices
        #  [d.get_mac() for d in devices]

    def _on_search_error(self, error):
        self.node_instance.logger.error(error)

    def list(self, timeout=5) -> list:
        #  不等待, 异步推送
        start_time = time.time()
        FusiSDK.search_devices(self._on_found_devices, self._on_search_error)
        # 等待 timeout
        while True:
            if self.devices:
                self.current_devices = self.devices
                self.devices = None  # 清理
                return [d.get_mac() for d in self.current_devices]
            else:
                if time.time() - start_time > timeout:
                    # 超时
                    return []
                else:
                    time.sleep(1)

    def connect(self, id, timeout=5):
        for d in self.current_devices:
            if id == d.get_mac():
                d.set_listener(MyListener(d, self.node_instance))
                # self.is_connected = True
                d.connect()

    def status(self, **kwargs) -> bool:
        pass

    def disconnect(self):
        self.is_connected = False
        self.thing = None
        self.node_instance.terminate()
        FusiSDK.dispose()  # 强制退出


class MyNode(AdapterNode):
    NODE_ID = "eim/node_brainCo"
    HELP_URL = "https://adapter.codelab.club/extension_guide/brainCo/"
    DESCRIPTION = "brainCo"
    VERSION = "1.1.0"
    
    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)
        self.thing = ThingProxy(self)

    def run_python_code(self, code):
        try:
            output = eval(
                code,
                {"__builtins__": None},
                {
                    # "thing": self.thing.thing,  # 直接调用方法
                    "connect": self.thing.connect,
                    "disconnect": self.thing.disconnect,
                    "list": self.thing.list,
                })
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'code: {payload["content"]}')
        python_code = payload["content"]
        output = self.run_python_code(python_code)
        try:
            output = json.dumps(output)
        except Exception:
            output = str(output)
        payload["content"] = output
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        while self._running:
            time.sleep(0.5)

    def terminate(self, **kwargs):
        try:
            self.thing.disconnect()
        except Exception:
            pass
        super().terminate(**kwargs)


def main(**kwargs):
    try:
        node = MyNode(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except Exception as e:
        if node._running:
            node.pub_notification(str(e), type="ERROR")
            time.sleep(0.1)
            node.terminate()

if __name__ == "__main__":
    main()