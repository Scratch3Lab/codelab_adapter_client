from codelab_adapter_client import HANode
import subprocess
import time

class Neverland(HANode):
    def __init__(self):
        super().__init__()

neverland = Neverland()
neverland.receive_loop_as_thread()
time.sleep(1)
all_light = neverland.list_all_light_entity_ids()
print(all_light)