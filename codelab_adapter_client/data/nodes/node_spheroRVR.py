'''
https://spherov2.readthedocs.io/en/latest/sphero_edu.html
'''
import time
import json
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.thing import AdapterThing
from codelab_adapter_client.utils import threaded

from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI
from spherov2.types import Color
from spherov2.toy.rvr import RVR
from bleak import BleakError

from codelab_adapter_client.config import settings
from loguru import logger
debug_log = str(settings.NODE_LOG_PATH / "spheroRVR.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class ThingProxy(AdapterThing):
    def __init__(self, node_instance):
        super().__init__(thing_name="Sphero RVR", node_instance=node_instance)
        self.toys = None

    def list(self, timeout=5) -> list:
        #  https://github.com/artificial-intelligence-class/spherov2.py/blob/a3979bdf4342fbdb660c49938af3a74a26045b19/spherov2/scanner.py#L27
        #  find_toys(toy_names=[toy_name] if toy_name else None, **kwargs)
        try:
            self.toys = scanner.find_toys(
                toy_types=[RVR])  # scanner.find_RVR()  # timeout, 多个的时候怎么做
            #  key value
            # toy.address id
            return [toy.address for toy in self.toys]  # address
        except BleakError as e:
            self.node_instance.pub_notification(str(e), type="ERROR")
            return []

    def _send_connect_reply(self):
        payload = self.node_instance.connect_payload
        message = {"payload": payload}
        self.node_instance.publish(message)

    def _send_disconnect_message(self):
        self.node_instance.pub_notification(
            f'{self.node_instance.NODE_ID} 已断开', type="WARNING")

    @threaded
    def _connect(self, toy):
        with SpheroEduAPI(toy) as droid:
            self.node_instance.logger.debug("send_connect_reply")
            self._send_connect_reply()
            self.thing = droid
            self.is_connected = True
            # 当前驱动不知何时断开
            # while toy.is_connected(): # 不存在bleak一样的观测信息
            # https://github.com/artificial-intelligence-class/spherov2.py/blob/a3979bdf4342fbdb660c49938af3a74a26045b19/spherov2/adapter/bleak_adapter.py#L14
            while self.is_connected:
                time.sleep(0.1)  # 只能自己看蓝牙
        # spherov2.controls.PacketDecodingException: Bad response checksum, 无所谓

    def connect(self, id, timeout=5):
        if self.toys:
            for toy in self.toys:
                if toy.address == id:
                    # connect 阻塞入口
                    self._connect(toy)
                    # time.sleep(3)  # 给足连接时间, todo 由 _connect发送
                    return True
        else:
            self.node_instance.pub_notification("未发现 RVR", type="ERROR")
            raise Exception("RVR not found")

    def status(self, **kwargs) -> bool:
        pass

    def disconnect(self):
        # 不要try，暴露问题
        self.is_connected = False
        self.thing = None
        time.sleep(0.5)


class MyNode(AdapterNode):
    NODE_ID = "eim/node_spheroRVR"
    HELP_URL = "https://adapter.codelab.club/extension_guide/spheroRVR/"
    DESCRIPTION = "thing Demo"  # list connect
    VERSION = "1.0.0"

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)
        self.thing = ThingProxy(self)
        self.connect_payload = None

    def run_python_code(self, code):
        try:
            output = eval(
                code,
                {"__builtins__": None},
                {
                    "rvr": self.thing.thing,  # 直接调用方法
                    "connect": self.thing.connect,
                    "disconnect": self.thing.disconnect,
                    "list": self.thing.list,
                    "Color": Color,
                })
            '''
                rvr.set_main_led(Color(r=0, g=0, b=255))
                rvr.set_speed(60)
                time.sleep(2)
                rvr.set_speed(0)
            '''
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        python_code = payload["content"]
        if python_code.startswith('connect('):
            # connect
            self.connect_payload = payload
        output = self.run_python_code(python_code)
        try:
            output = json.dumps(output)
        except Exception:
            output = str(output)
        # 单独处理connect，异步连接
        if not python_code.startswith('connect('):
            # connect 连上之后（异步）发送
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