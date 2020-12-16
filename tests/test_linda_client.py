'''
py.test tests/test_linda.py  -s

Adapter运行之后，跑测试
'''

import time
import asyncio
# import pytest
from codelab_adapter_client import AdapterNodeAio
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import LindaTimeoutError

class MyNode(AdapterNodeAio):
    NODE_ID = "eim/extension_python"

    def __init__(self):
        super().__init__()

class MySyncNode(AdapterNode):
    NODE_ID = "eim/node_alphamini"

    def __init__(self):
        super().__init__()

async def _async_test_main(node):    
    task = asyncio.create_task(node.receive_loop()) # todo: 潜在 bug
    await asyncio.sleep(0.1) # 等待管道建立
    _tuple = ["test_linda"]
    # reboot 
    res = await node.linda_reboot()
    assert res == []

    # out
    tuple_number = 3
    for i in range(tuple_number):
        _tuple = [i]
        res = await node.linda_out(_tuple)
        assert res == _tuple
    
    # dump
    res = await node.linda_dump()
    print(res)
    assert res == [[i] for i in range(tuple_number)]

    # rd
    _tuple = [1]
    res = await node.linda_rd(_tuple)
    assert res == _tuple

    # in
    for i in range(tuple_number):
        _tuple = [i]
        res = await node.linda_in(_tuple)
        assert res == _tuple
    # 消耗完

    
    # 生成新的
    _tuple = ["hello", "world"]
    await node.linda_out(_tuple)

    # rdp
    res = await node.linda_rdp(_tuple)
    assert res == _tuple

    # inp
    res = await node.linda_inp(_tuple)
    assert res == _tuple

    res = await node.linda_dump()
    assert res == []
    # in

    await node.terminate()

def test_async_linda_client():
    node = MyNode()
    asyncio.run(_async_test_main(node))


def test_sync_linda_client():
    node = MySyncNode()
    node.receive_loop_as_thread()
    time.sleep(0.1)

    res = node.linda_reboot()
    assert res == []

    res = node.linda_out([1, 2, 3]) # out
    assert res == [1, 2, 3]

    res = node.linda_out([1, 2, 4]) # out
    res = node.linda_dump()
    assert res == [[1, 2, 3], [1, 2, 4]]
    
    res = node.linda_rd([1, 2, 3])
    assert res == [1, 2, 3]

    res = node.linda_rdp([1, 2, "*"])
    assert res == [1, 2, 3] # 先入先出

    res = node.linda_in([1,2,3])
    assert res == [1, 2, 3]

    res = node.linda_dump()
    assert res == [[1, 2, 4]]

    res = node.linda_inp(["xxx"])
    assert res == []

    res = node.linda_inp([1, "*", 4])
    assert res == [1, 2, 4]

    res = node.linda_reboot()
    assert res == []



    
    # 创建
    # print("find_microbit: ",utils.find_microbit())
