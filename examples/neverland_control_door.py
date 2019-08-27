from codelab_adapter_client import HANode
import time

class Neverland(HANode):
    def __init__(self):
        super().__init__()

    def open_door(self):
        self.call_service(
            service="turn_on",
            domain="switch",
            entity_id="switch.0x00158d0001b774fd_switch_l1")

    def close_door(self):
        self.call_service(
            service="turn_off",
            domain="switch",
            entity_id="switch.0x00158d0001b774fd_switch_l1")
 
neverland = Neverland()
neverland.open_door()
time.sleep(5)
neverland.close_door()