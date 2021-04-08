import queue
import time
import rumps
# import pyautogui  # todo 自动安装
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.topic import NODES_OPERATE_TOPIC
from codelab_adapter_client.utils import install_requirement, open_webui

class StatusBarNode(AdapterNode):
    '''
    Everything Is Message
    ref: https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/extensions_v2/extension_python_kernel.py
    '''
    NODE_ID = "eim/node_status_bar_mac"
    HELP_URL = "https://adapter.codelab.club/extension_guide/status_bar/"
    DESCRIPTION = "mac status bar"
    REQUIREMENTS = ["rumps"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.q = queue.Queue()

    def extension_message_handle(self, topic, payload):
        pass

    def run(self):
        Node = self

        class AwesomeStatusBarApp(rumps.App):
            # quit 整个程序终止了
            # todo 退出 Adapter
            @rumps.clicked("Open WebUI")
            def webui(self, _):
                open_webui()

            @rumps.clicked("Exit Adapter")
            def exit(self, _):
                # rumps.notification("Awesome title", "amazing subtitle", "hi!!1")
                payload = {
                    "content": 'stop',
                    "node_id": "all",
                    "node_name": "_"
                }  # todo message template
                # 变量的可见性 ：），坏习惯
                Node.publish_payload(payload, NODES_OPERATE_TOPIC)  # 发送给
                time.sleep(0.2)
                rumps.quit_application()

        AwesomeStatusBarApp(
            "🔥", #
            quit_button=None).run()  # 可通过 rumps.quit_application() 退出
        # status bar 退出， 触发adapter的结束机制
        # 像前端一样发送
        self.terminate()

    def terminate(self, stop_cmd_message_id=None):
        try:
            rumps.quit_application()
        except:
            pass
        super().terminate(stop_cmd_message_id=stop_cmd_message_id)


def main(**kwargs):
    # 多进程启动，todo 启动 message id
    try:
        node = StatusBarNode(**kwargs)
        node.receive_loop_as_thread()
        # node._import_requirement_or_import()  # run 之前导入namespace
        node.run()  # 拦截ctrl-c
    except KeyboardInterrupt:
        node.logger.debug("KeyboardInterrupt")
        node.terminate()  # Clean up before exiting.
    except Exception as e:
        node.logger.error(str(e))
        node.pub_notification(str(e), type="ERROR")
        time.sleep(0.05)
        node.terminate()  # Clean up before exiting.
        # rumps.quit_application()


if __name__ == "__main__":
    main()