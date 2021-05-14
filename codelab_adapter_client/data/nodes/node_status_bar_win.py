'''
PySimpleGUI
    https://pysimplegui.readthedocs.io/
    https://github.com/PySimpleGUI/PySimpleGUI/tree/master/PySimpleGUIWx
mac build后有问题
'''

import PySimpleGUIWx as sg
import time
import sys
import pathlib
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.topic import NODES_OPERATE_TOPIC
from codelab_adapter_client.utils import is_win, open_webui, open_path

codelab_adapter_dir = pathlib.Path.home() / "codelab_adapter"
app_icon = str(
    codelab_adapter_dir / 'src') + "/app." + ('ico' if is_win() else 'png')
tray = sg.SystemTray(menu=['menu', ['Open WebUi', 'Open Adapter Home', 'E&xit']], filename=app_icon)
# tray.ShowMessage('My Message', 'The tray icon is up and runnning!')


class MyNode(AdapterNode):
    NODE_ID = "eim/node_status_bar_win"
    # HELP_URL = "https://adapter.codelab.club/extension_guide/status_bar/"
    DESCRIPTION = "status bar"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def terminate(self, stop_cmd_message_id=None):
        print("terminate")
        super().terminate(stop_cmd_message_id=stop_cmd_message_id)


def main(**kwargs):
    node = MyNode(**kwargs)
    node.receive_loop_as_thread()  # wait for terminate
    # 要在主进程里?
    while node._running:
        event = tray.Read(timeout=500)  # 500ms
        # print(event)
        if event == 'Exit':
            payload = {
                "content": 'stop',
                "node_id": "all",
                "node_name": "_"
            }  # todo message template
            node.publish_payload(payload, NODES_OPERATE_TOPIC)
            time.sleep(0.2)
            break
        if event == 'Open WebUi':
            # sg.popup('Menu item chosen', menu_item)
            open_webui()

        if event == 'Open Adapter Home':
            # sg.popup('Menu item chosen', menu_item)
            open_path(codelab_adapter_dir)
            


if __name__ == "__main__":
    main()