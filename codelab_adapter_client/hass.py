# HA
from .base import AdapterNode
from codelab_adapter_client.topic import *
from collections import deque
import time
from loguru import logger


class HANode(AdapterNode):
    '''
    使用继承的目的是让新手获得专家的能力 -- alan kay
    real playing

    todo 获取设备状态
    '''

    def __init__(self, *args, mode="rpi", **kwargs):
        '''
        mode rpi/local
        '''
        if mode:
            kwargs["codelab_adapter_ip_address"] = "rpi.codelab.club"
        kwargs["logger"] = logger
        super().__init__(*args, **kwargs)
        self.TOPIC = TO_HA_TOPIC  # after super init
        self.set_subscriber_topic(FROM_HA_TOPIC)
        self._message_id = 1
        self.ha_message_queue = deque(maxlen=2)
        self.target_entity_ids = ["door", "cube"]

    def call_service(self,
                     domain="light",
                     service="turn_off",
                     entity_id="light.yeelight1"):
        content = {
            "id": self._message_id,
            "type": "call_service",
            "domain": domain,
            "service": service,
            "service_data": {
                "entity_id": entity_id
            }
        }
        self._message_id += 1
        message = self.message_template()
        message['payload']['content'] = content
        self.publish(message)

    def message_handle(self, topic, payload):
        '''
        '''
        if topic == FROM_HA_TOPIC:
            timestamp = time.time()

            # HA部分只订阅了状态变化事件
            content = payload.get("content")
            event_type = content["type"]
            if event_type == "event":
                '''
                with open('/tmp/neverland.json', 'w+') as logfile:
                        print(payload, file=logfile)
                '''
                data = content["event"]["data"]
                entity_id = data["entity_id"]
                if any([
                        target_entity_id in entity_id
                        for target_entity_id in self.target_entity_ids
                ]):

                    new_state = data["new_state"]["state"]
                    old_state = data["old_state"]["state"]
                    self.ha_message_queue.append((timestamp, payload))
                    if len(self.ha_message_queue) == 2:
                        latest_message_timestamp = self.ha_message_queue[1][0]
                        old_message_timestamp = self.ha_message_queue[0][0]
                        elapsed = latest_message_timestamp - old_message_timestamp
                        # print("elapsed:", elapsed)
                        self.logger.debug(
                            f'old_state:{old_state}, new_state:{new_state}'
                        )  # 观察，数据

                        if "door" in entity_id:
                            '''
                            开门
                              old_state:off, new_state:on
                            关门
                              old_state:on, new_state:off

                            模仿gpiozero
                            '''
                            method_name = None
                            entity = "door"
                            action = None
                            if (old_state, new_state) == ("off", "on"):
                                # print("open door")
                                action = "open"
                            if (old_state, new_state) == ("on", "off"):
                                action = "close"
                                # print("close door")
                            method_name = f"{action}_{entity}"
                            if action:
                                self.user_event_method(method_name, entity,
                                                       action)

                        if "cube" in entity_id:
                            '''
                            old_state:, new_state:rotate_left
                            '''
                            method_name = None
                            entity = "cube"
                            action = None
                            if (not old_state) and new_state:
                                action = new_state
                                method_name = f"{action}_{entity}"
                                if action:
                                    self.user_event_method(
                                        method_name, entity, action)

    def user_event_method(self, method_name, entity, action):
        if hasattr(self, method_name):
            getattr(self, method_name)()

        if hasattr(self, "neverland_event"):
            getattr(self, "neverland_event")(entity, action)  # entity action
