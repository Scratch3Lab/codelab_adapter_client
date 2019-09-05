# HA
from .base import AdapterNode
from codelab_adapter_client.topic import *
import time
from loguru import logger
import random

GET_STATES = "get_states"


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
        # self._message_id = 1  # HA server处理id
        self.target_entity_ids = ["door", "cube"]
        self.states = None
        self.lights = None
        self.switches = None
        self.get_states()

    def list_all_light_entity_ids(self):
        return self.lights

    def list_all_switch_entity_ids(self):
        return self.switches

    def get_states(self):
        get_states_message = {
            "type": GET_STATES,
        }
        message = self.message_template()
        message['payload']['content'] = get_states_message
        self.publish(message)

    def call_service(self,
                     domain="light",
                     service="turn_off",
                     entity_id="light.yeelight1"):
        content = {
            "type": "call_service",
            "domain": domain,
            "service": service,
            "service_data": {
                "entity_id": entity_id
            }
        }
        message = self.message_template()
        message['payload']['content'] = content
        self.publish(message)

    def message_handle(self, topic, payload):
        '''
        '''
        if topic == FROM_HA_TOPIC:
            message_id = payload["content"]["id"]
            mytype = payload["content"].get("mytype")
            if mytype == GET_STATES:
                # 建议 使用IPython交互式探索
                self.states = payload["content"]
                result = payload["content"]["result"]
                for i in result:
                    if i["entity_id"] == "group.all_lights":
                        self.lights = i["attributes"]["entity_id"]
                    if i["entity_id"] == "group.all_switches":
                        self.switches = i["attributes"]["entity_id"]

            # HA部分只订阅了状态变化事件, get_states单独处理
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
                        method_name = f"when_{action}_{entity}"  # when open door
                        if action:
                            self.user_event_method(method_name, entity, action,
                                                   entity_id)

                    if "cube" in entity_id:
                        '''
                            old_state:, new_state:rotate_left
                            '''
                        method_name = None
                        entity = "cube"
                        action = None
                        if (not old_state) and new_state:
                            action = new_state
                            method_name = f"when_{action}_{entity}"
                            if action:
                                self.user_event_method(method_name, entity,
                                                       action, entity_id)

    def user_event_method(self, method_name, entity, action, entity_id):
        if hasattr(self, method_name):
            getattr(self, method_name)()

        if hasattr(self, "neverland_event"):
            getattr(self, "neverland_event")(entity, action,
                                             entity_id)  # entity action
