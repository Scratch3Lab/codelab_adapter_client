import asyncio
from codelab_adapter_client import MessageNodeAio

class TestNode(MessageNodeAio):
    def __init__(self,event_loop):
            super().__init__(event_loop=event_loop)

loop = asyncio.get_event_loop()
test_node = TestNode(loop)
# loop
async def hello_world():
    while True:
        await asyncio.sleep(1)

loop.run_until_complete(hello_world())