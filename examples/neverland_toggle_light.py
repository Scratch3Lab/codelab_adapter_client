from codelab_adapter_client import HANode


class Neverland(HANode):
    def __init__(self):
        super().__init__()


neverland = Neverland()

neverland.call_service(service="toggle")

# neverland.call_service(service="turn_off",domain="switch", entity_id="switch.0x00158d0002ecce03_switch_right")
