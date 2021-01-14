'''
Adapter Thing
与具体设备通信，对外提供服务

以
    node_alphamini
    node_yeelight
    extension_usb_microbit
为原型

需要实现一些抽象接口(与外部交互)
    list
    connect
    status
    disconnect
    
'''
from abc import abstractmethod, ABCMeta

class AdapterThing(metaclass=ABCMeta):
    '''
    class Robot(AdapterThingAio):
        def __init__(self, node_instance):
            super().__init__(node_instance)

        async def list(self):
            print("list robot")

        def connect(self):
            print("list robot")
        
        def disconnect(self):
            print("list robot")
    '''
    def __init__(self, thing_name, node_instance):
            self.node_instance = node_instance
            self.is_connected = False  
            self.thing_name = thing_name
            self.thing = None
            
    
    def _ensure_connect(self):
        # 确认某件事才往下，否则返回错误信息, 意外时将触发
        if not self.is_connected:
            raise Exception("{self.thing_name} not connected!")
    
    @abstractmethod
    def list(self, **kwargs): # 可以是 async
        # connect things
        '''please Implemente in subclass'''
    
    @abstractmethod
    def connect(self, **kwargs) -> bool:
        # connect thing
        '''please Implemente in subclass'''

    @abstractmethod
    def status(self, **kwargs) -> bool:
        # query thing status
        '''please Implemente in subclass'''
    

    @abstractmethod
    def disconnect(self, **kwargs) -> bool:
        # disconnect things
        '''please Implemente in subclass'''

