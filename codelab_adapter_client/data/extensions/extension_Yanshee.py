'''
https://github.com/UBTEDU/Yan_ADK
http://192.168.31.109:9090/v1/ui/#!/devices/get_devices_battery
https://app.swaggerhub.com/apis-docs/UBTEDU/apollo_cn/1.0.0#/devices/getDevicesVersions

todo
    使用rest api， 不用 openadk

调试技巧
    直接使用python 在terminal里运行 node 插件
'''
import sys
import time
import os  # env

import requests
from codelab_adapter.core_extension import Extension


class Robot:
    def __init__(self, node=None):
        self.node = node
        self.is_connected = False
        self.robot_uri = None

    def _get(self, path, payload):
        '''
        >>> payload = {'key1': 'value1', 'key2': 'value2'}
        >>> r = requests.get('https://httpbin.org/get', params=payload)
        '''
        url = f"{self.robot_uri}{path}"
        r = requests.get(url, params=payload)
        return r

    def _put(self, path, payload):
        '''
        >>> url = 'https://api.github.com/some/endpoint'
        >>> payload = {'some': 'data'}
        >>> r = requests.post(url, json=payload)
        '''
        url = f"{self.robot_uri}{path}"
        r = requests.put(url, json=payload)
        return r

    def connect(self, robot_ip="raspberrypi.local"):
        # 如果未完成，则对robot的调用都弹出提醒
        self.robot_uri = f'http://{robot_ip}:9090/v1'  # /ui
        if self.ping_robot() == "online":
            if self.node:
                self.node.pub_notification("Yanshee 已连接",
                                           type="SUCCESS")  # 由一个积木建立连接到时触发
            self.is_connected = True
            return True

    def get_battery(self):
        path = "/devices/battery"
        payload = {}
        r = self._get(path, payload)
        return r.json()["data"]["percent"]

    def get_versions(self):
        path = f"/devices/versions"  # get version
        payload = {'type': 'core'}
        r = self._get(path, payload)
        return r
        
    # todo 装饰器 require connect
    def ping_robot(self):
        # get versions
        r = self.get_versions()
        if r.status_code == 200:
            return "online"

    def put_motions(self, **kwargs):
        '''
        name="wave",  
        operation='start',
        direction='both',
        speed="fast"):
        '''
        path = "/motions"
        # update payload
        operation = kwargs.pop("operation", "start")
        motion = {
            "name":
            "wave",  # # GetUp, Hug, Bow , HappyBirthday, Forward Backward OneStepForward TurnLeft TurnRight
            # "direction": "both",
            # "repeat": 1,
            "speed": "fast"  # # ['start', 'pause', 'resume', 'stop']
        }
        motion.update(kwargs)
        payload = {
            "operation": operation,  # start pause continue stop
            "motion": motion,
            "timestamp": int(time.time())
        }
        r = self._put(path, payload)
        return r

    def play(self, **kwargs):  # 兼容
        return self.put_motions(**kwargs)

    def bow(self):
        # robot.play(name="bow",speed="slow",operation="start")
        if not self.is_connected:
            return
        return self.play(name="bow",
                         speed="slow",
                         operation="start")

    def say(self, content="你好"):
        if not self.is_connected:
            return
        path = "/voice/tts"
        payload = {
            "tts": content,
            "interrupt": True,
            "timestamp": int(time.time())
        }
        r = self._put(path, payload)
        return r


class YansheeExtension(Extension):
    NODE_ID = "eim/extension_Yanshee"
    HELP_URL = "https://adapter.codelab.club/extension_guide/yanshee/"
    DESCRIPTION = "基于树莓派的开放机器人平台"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.robot = Robot(self)

    def run_python_code(self, code):
        try:
            output = eval(
                code,
                {"__builtins__": None},
                {
                    # "api_instance": self.robot.api_instance,
                    "robot": self.robot
                })
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        # todo 判断是否连接成功，否则报告连接问题

        self.logger.info(f'code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]

        # 检查是否连接
        if (not self.robot.is_connected) and ("connect" not in python_code):
            self.pub_notification("未发现 Yanshee",
                                  type="WARNING")
            return

        output = self.run_python_code(python_code)
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        while self._running:
            time.sleep(0.5)


export = YansheeExtension
