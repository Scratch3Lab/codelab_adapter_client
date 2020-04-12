from codelab_adapter_client import HANode


class Neverland(HANode):
    def __init__(self):
        super().__init__()


neverland = Neverland()

# neverland.call_service(service="toggle")

neverland.call_service(service="turn_on",domain="vacuum", entity_id="vacuum.roomba")
# service: start_pause stop return_to_base