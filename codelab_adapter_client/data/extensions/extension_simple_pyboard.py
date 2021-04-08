import time

from codelab_adapter.core_extension import Extension
from codelab_adapter.pyb_adapter import SimplePyboardHelper
import codelab_adapter

class SerialExtension(Extension):

    NODE_ID = "eim/extension_simple_pyboard"
    HELP_URL = "http://adapter.codelab.club/extension_guide/SimplePyboard/"
    VERSION = "1.0"  # extension version
    DESCRIPTION = "Simple Pyboard(掌控板/bpi:bit/esp32/esp8266/microbit/...)"
    WEIGHT = 93

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.simplePyboardHelper = SimplePyboardHelper(self)

    def run_python_code(self, code):
        try:
            output = eval(code, {"__builtins__": None}, {
                "simplePyboardHelper": self.simplePyboardHelper,
            })
        except codelab_adapter.pyb.PyboardError as e:
            output = str(e)
        except Exception as e:
            output = str(e)
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'python code: {payload["content"]}')
        message_id = payload.get("message_id")
        code = payload["content"]
        if "simplePyboardHelper" in code:
            output = self.run_python_code(code)  # scan / connect / flash
            payload["content"] = output
            message = {"payload": payload}
            self.publish(message)

        elif self.simplePyboardHelper.is_connected:
            # eval in the pyboard
            output = self.simplePyboardHelper.send_command(code)
            payload["content"] = output
            message = {"payload": payload}
            self.publish(message)

        else:
            self.pub_notification("未发现 MicroPython 设备", type="ERROR")

    def run(self):
        "避免插件结束退出"
        while self._running:
            time.sleep(0.5)


export = SerialExtension
