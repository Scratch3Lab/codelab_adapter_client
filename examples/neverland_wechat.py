'''
python >= 3.6
pip install itchat codelab_adapter_client
'''
import itchat
from codelab_adapter_client import HANode

class Neverland(HANode):
    def __init__(self):
        super().__init__()

neverland = Neverland()

@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    if msg.text == "开灯":
        neverland.call_service(service="turn_on")
        msg.user.send("已开灯")
    if msg.text == "关灯":
        neverland.call_service(service="turn_off")
        msg.user.send("已关灯")


# neverland.call_service(service="turn_off",domain="switch", entity_id="switch.0x00158d0002ecce03_switch_right")
itchat.auto_login(hotReload=True)
itchat.run()