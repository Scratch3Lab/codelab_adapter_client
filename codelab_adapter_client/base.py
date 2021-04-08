import time
import logging
import sys
import uuid
import os
from abc import ABCMeta, abstractmethod
from pathlib import Path
import argparse
import concurrent.futures

import msgpack
import zmq
# import psutil
from codelab_adapter_client.config import settings
from codelab_adapter_client.topic import *
from codelab_adapter_client.utils import threaded, TokenBucket, LindaTimeoutError, NodeTerminateError, LindaOperate
from codelab_adapter_client._version import protocol_version
from codelab_adapter_client.session import _message_template

logger = logging.getLogger(__name__)

SPEED_DEBUG = False

class MessageNode(metaclass=ABCMeta):
    # jupyter client Session: https://github.com/jupyter/jupyter_client/blob/master/jupyter_client/session.py#L249
    def __init__(
        self,
        name='',
        logger=logger,
        codelab_adapter_ip_address=None,
        subscriber_port='16103',
        publisher_port='16130',  #write to conf file(jupyter)
        subscriber_list=[SCRATCH_TOPIC, NODES_OPERATE_TOPIC, LINDA_CLIENT],
        loop_time=settings.ZMQ_LOOP_TIME,
        connect_time=0.1,
        external_message_processor=None,
        receive_loop_idle_addition=None,
        token=None,
        bucket_token=100,
        bucket_fill_rate=100,
        recv_mode = "noblock",
        ):
        '''
        :param codelab_adapter_ip_address: Adapter IP Address -
                                      default: 127.0.0.1
        :param subscriber_port: codelab_adapter subscriber port.
        :param publisher_port: codelab_adapter publisher port.
        :param loop_time: Receive loop sleep time.
        :param connect_time: Allow the node to connect to adapter
        :param token: for safety
        :param bucket_token/bucket_fill_rate: rate limit
        '''
        self.last_pub_time = time.time
        self.bucket_token = bucket_token
        self.bucket_fill_rate = bucket_fill_rate
        self.recv_mode = recv_mode
        self.bucket = TokenBucket(bucket_token, bucket_fill_rate)
        self.logger = logger
        self._running = True  # use it to control Python thread, work with self.terminate()
        if name:
            self.name = name
        else:
            self.name = type(self).__name__  # instance name(self is instance)
        self.token = token
        self.subscriber_port = subscriber_port
        self.publisher_port = publisher_port
        self.subscriber_list = subscriber_list
        self.subscribed_topics = set(
        )  # genetate sub topics self.subscribed_topics.add
        self.receive_loop_idle_addition = receive_loop_idle_addition
        self.external_message_processor = external_message_processor
        self.connect_time = connect_time
        if codelab_adapter_ip_address:
            self.codelab_adapter_ip_address = codelab_adapter_ip_address
        else:
            # check for a running CodeLab Adapter
            # self.check_adapter_is_running()
            # determine this computer's IP address
            self.codelab_adapter_ip_address = '127.0.0.1'
        self.loop_time = loop_time

        self.logger.info(
            '\n************************************************************')
        self.logger.info('CodeLab Adapter IP address: ' +
                         self.codelab_adapter_ip_address)
        self.logger.info('Subscriber Port = ' + self.subscriber_port)
        self.logger.info('Publisher  Port = ' + self.publisher_port)
        self.logger.info('Loop Time = ' + str(loop_time) + ' seconds')
        self.logger.info(
            '************************************************************')

        # establish the zeromq sub and pub sockets and connect to the adapter
        self.context = zmq.Context()
        # 以便于一开始就发送消息，尽管连接还未建立
        self.publisher = self.context.socket(zmq.PUB)
        pub_connect_string = f'tcp://{self.codelab_adapter_ip_address}:{self.publisher_port}'
        self.publisher.connect(pub_connect_string)
        # Allow enough time for the TCP connection to the adapter complete.
        time.sleep(self.connect_time /
                   2)  # block 0.3 -> 0.1, to support init pub

    def __str__(self):
        return self.name

    def is_running(self):
        return self._running

    '''
    def check_adapter_is_running(self):
        adapter_exists = False
        for pid in psutil.pids():
            p = psutil.Process(pid)
            try:
                p_command = p.cmdline()
            except psutil.AccessDenied:
                # occurs in Windows - ignore
                continue
            try:
                if any('codelab' in s.lower() for s in p_command):
                    adapter_exists = True
                else:
                    continue
            except UnicodeDecodeError:
                continue

        if not adapter_exists:
            raise RuntimeError(
                'CodeLab Adapter is not running - please start it.')
    '''

    def set_subscriber_topic(self, topic):
        if not type(topic) is str:
            raise TypeError('Subscriber topic must be string')
        self.subscriber_list.append(topic)

    def publish_payload(self, payload, topic=''):
        if not type(topic) is str:
            raise TypeError('Publish topic must be string', 'topic')

        if self.bucket.consume(1):
            # pack
            message = msgpack.packb(payload, use_bin_type=True)

            pub_envelope = topic.encode()
            if SPEED_DEBUG:
                self.logger.debug(f"SPEED_DEBUG-publish_payload: {time.time()}")
            self.publisher.send_multipart([pub_envelope, message])
        else:
            now = time.time()
            if (now - self.last_pub_time > 1):
                error_text = f"发送消息过于频繁!({self.bucket_token}, {self.bucket_fill_rate})" # 1 /s or ui
                self.logger.error(error_text)
                self.pub_notification(error_text, type="ERROR")
                self.last_pub_time = time.time() 

    def receive_loop(self):
        """
        This is the receive loop for receiving sub messages.
        """
        self.subscriber = self.context.socket(zmq.SUB)
        sub_connect_string = f'tcp://{self.codelab_adapter_ip_address}:{self.subscriber_port}'
        self.subscriber.connect(sub_connect_string)

        if self.subscriber_list:
            for topic in self.subscriber_list:
                self.subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode())
                self.subscribed_topics.add(topic)

        while self._running:
            try:
                # https://github.com/jupyter/jupyter_client/blob/master/jupyter_client/session.py#L814
                if self.recv_mode == "noblock":
                    data = self.subscriber.recv_multipart(zmq.NOBLOCK)  # NOBLOCK
                else:
                    data = self.subscriber.recv_multipart()
                # unpackb
                try:
                    # some data is invalid
                    topic = data[0].decode()
                    payload = msgpack.unpackb(data[1],
                                              raw=False)  # replace unpackb
                    self.message_handle(topic, payload)
                except Exception as e:
                    self.logger.error(str(e))
                # 这里很慢
                # self.logger.debug(f"extension.receive_loop -> {time.time()}")
            # if no messages are available, zmq throws this exception
            except zmq.error.Again:
                try:
                    if self.receive_loop_idle_addition:
                        self.receive_loop_idle_addition()
                    time.sleep(self.loop_time)
                except KeyboardInterrupt:
                    self.clean_up()
                    raise KeyboardInterrupt
            '''
            except msgpack.exceptions.ExtraData as e:
                self.logger.error(str(e))
            '''

    def receive_loop_as_thread(self):
        # warn: zmq socket is not threadsafe
        threaded(self.receive_loop)()

    def message_handle(self, topic, payload):
        """
        Override this method with a custom adapter message processor for subscribed messages.
        """
        print(
            'message_handle method should provide implementation in subclass.')

    def clean_up(self):
        """
        Clean up before exiting.
        """
        self._running = False
        time.sleep(0.1)
        # todo 等待线程退出后再回收否则可能出错
        self.publisher.close()
        self.subscriber.close()
        self.context.term()


class AdapterNode(MessageNode):
    '''
    CodeLab Adapter Node

    Adapter Extension is subclass of AdapterNode

    message_types = [
        "notification", "from_scratch", "from_adapter", "current_extension"
    ]
    '''
    def __init__(self,
                 start_cmd_message_id=None,
                 is_started_now=True,
                 *args,
                 **kwargs):
        '''
        :param codelab_adapter_ip_address: Adapter IP Address -
                                      default: 127.0.0.1
        :param subscriber_port: codelab_adapter subscriber port.
        :param publisher_port: codelab_adapter publisher port.
        :param loop_time: Receive loop sleep time.
        :param connect_time: Allow the node to connect to adapter
        '''
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'TOPIC'):
            self.TOPIC = ADAPTER_TOPIC  # message topic: the message from adapter
        if not hasattr(self, 'NODE_ID'):
            self.NODE_ID = "eim"
        if not hasattr(self, 'HELP_URL'):
            self.HELP_URL = "http://adapter.codelab.club/extension_guide/introduction/"
        if not hasattr(self, 'WEIGHT'):
            self.WEIGHT = 0
        # todo  handler: https://github.com/offu/WeRoBot/blob/master/werobot/robot.py#L590
        # self._handlers = {k: [] for k in self.message_types}
        # self._handlers['all'] = []

        if not start_cmd_message_id:
            '''
            1 node from cmd（start_cmd_message_id in args） 以脚本运行
                1.1 if __name__ == '__main__':
                1.2 采用命令行参数判断，数量内容 更精准，因为ide也是使用脚本启动
            2 extension from param（with start_cmd_message_id）
            3 work with jupyter/mu
            '''
            if "--start-cmd-message-id" in sys.argv:
                    parser = argparse.ArgumentParser()
                    parser.add_argument("--start-cmd-message-id", dest="message_id", default=None,
                                help="start cmd message id, a number or uuid(string)")
                    args = parser.parse_args()
                    start_cmd_message_id = args.message_id
        else:
            pass # extensions

        self.start_cmd_message_id = start_cmd_message_id 
        self.logger.debug(f"start_cmd_message_id -> {self.start_cmd_message_id}")
        if is_started_now and self.start_cmd_message_id:
            self.started()
        
        # linda
        self.linda_wait_futures = []

    def started(self):
        '''
        started notify
        '''
        self.pub_notification(f"启动 {self.NODE_ID}")
        # request++ and uuid, Compatible with them.
        try:
            int_message = int(self.start_cmd_message_id)
            self.send_reply(int_message)
        except ValueError:
            self.send_reply(self.start_cmd_message_id)

    def send_reply(self, message_id, content="ok"):
        response_message = self.message_template()
        response_message["payload"]["message_id"] = message_id
        response_message["payload"]["content"] = content
        self.publish(response_message)

    '''
    def add_handler(self, func, type='all'):
        # add message handler to Extension instance。
        # :param func:  handler method
        # :param type: handler type

        # :return: None

        if not callable(func):
            raise ValueError("{} is not callable".format(func))

        self._handlers[type].append(func)

    def get_handlers(self, type):
        return self._handlers.get(type, []) + self._handlers['all']

    def handler(self, f):
        # add handler to every message.

        self.add_handler(f, type='all')
        return f
    '''

    def generate_node_id(self, filename):
        '''
        extension_eim.py -> extension_eim
        '''
        node_name = Path(filename).stem
        return self._node_name_to_node_id(node_name)

    def _node_name_to_node_id(self, node_name):
        return f'eim/{node_name}'

    # def extension_message_handle(self, f):
    def extension_message_handle(self, topic, payload):
        """
        the decorator for adding current_extension handler
        
        self.add_handler(f, type='current_extension')
        return f
        """
        self.logger.info("please set the  method to your handle method")

    def exit_message_handle(self, topic, payload):
        self.pub_extension_statu_change(self.NODE_ID, "stop")
        if self._running:
            stop_cmd_message_id = payload.get("message_id", None)
            self.terminate(stop_cmd_message_id=stop_cmd_message_id)

    def message_template(self):
        # _message_template(sender,node_id,token)
        template = _message_template(self.name, self.NODE_ID, self.token)
        return template

    def publish(self, message):
        assert isinstance(message, dict)
        topic = message.get('topic')
        payload = message.get("payload")
        if not topic:
            topic = self.TOPIC
        if not payload.get("node_id"):
            payload["node_id"] = self.NODE_ID
        self.logger.debug(
            f"{self.name} publish: topic: {topic} payload:{payload}")

        self.publish_payload(payload, topic)

    ########################
    # todo linda mixin
    def _send_to_linda_server(self, operate, _tuple):
        '''
        send to linda server and wait it （client block / future）
        return:
            message_id
        '''
        assert isinstance(operate, LindaOperate)
        assert isinstance(_tuple, list)
        if not self._running:
            # loop
            Exception(f"_running: {self._running}") 

        topic = LINDA_SERVER # to 

        payload = self.message_template()["payload"]
        payload["message_id"] = uuid.uuid4().hex
        payload["operate"] = operate.value # 将枚举数据变成序列化
        payload["tuple"] = _tuple
        payload["content"] = _tuple # 是否必要
        
        self.logger.debug(
            f"{self.name} publish: topic: {topic} payload:{payload}")

        self.publish_payload(payload, topic)
        return payload["message_id"]


    def _send_and_wait_origin(self, operate, _tuple, timeout):
        '''
        失败之后out东西
        '''
        # 确保 running， 接收到消息
        message_id = self._send_to_linda_server(operate, _tuple)
        '''
        return future timeout
        futurn 被消息循环队列释放
        '''
        f = concurrent.futures.Future()
        self.linda_wait_futures.append((message_id, f))
        # todo 加入到队列里: (message_id, f) f.set_result(tuple)
        try:
            result = f.result(timeout=timeout)
            return result
        except concurrent.futures.TimeoutError:
            # result = f"timeout: {timeout}"
            # todo 结构化
            raise LindaTimeoutError(f'timeout: {timeout}; message_id: {message_id}')
        # todo exit exception
        # return result

    def _send_and_wait(self, operate, _tuple, timeout):
        try:
            return self._send_and_wait_origin(operate, _tuple, timeout)
        except:
            if operate in [LindaOperate.IN]:
                self.logger.warning(f'cancel: {operate} {_tuple}')
                self._send_to_linda_server(LindaOperate.OUT, _tuple) # 不等回复
                time.sleep(0.01)

    def linda_in(self, _tuple: list, timeout=None):
        '''
        timeout 心理模型不好，尽量不用，timeout之后，linda server还在维护 in_queue
        尽量使用inp
        # https://docs.python.org/zh-cn/3/library/typing.html
        params:
            _tuple: list
        linda in
        block , 不要timeout？
        todo 
            返回future，由用户自己决定是否阻塞？ callback
            参数 return_future = False
        
        todo 
            如果中断取消呢？
                粗糙的做法 out 出去
        '''
        return self._send_and_wait(LindaOperate.IN, _tuple, timeout)

    def linda_inp(self, _tuple: list):
        return self._send_and_wait(LindaOperate.INP, _tuple, None)


    # 阻塞吗？
    def linda_rd(self, _tuple: list, timeout=None):
        '''
        rd 要能够匹配才有意思， 采用特殊字符串，匹配

        如果当前没有 client 要等待吗（服务端如果看到相同的会再次发送，不等待的服务端返回 [], 先做阻塞的），行为在client决定，已经收到通知了
        '''
        return self._send_and_wait(LindaOperate.RD, _tuple, timeout)

    def linda_rdp(self, _tuple: list):
        return self._send_and_wait(LindaOperate.RDP, _tuple, None)


    def linda_out(self, _tuple, wait=True):
        # 限制速率， 每秒30帧
        # out 是否也确认，以此限制速率，确保收到
        # self._send_to_linda_server(LindaOperate.OUT, _tuple)
        if wait:
            return self._send_and_wait(LindaOperate.OUT, _tuple, None)
        else:
            return self._send_to_linda_server(LindaOperate.OUT, _tuple) # message id 回执
        


    # helper , 立刻返回
    def linda_dump(self):
        timeout=None
        return self._send_and_wait(LindaOperate.DUMP, ["dump"], timeout)

    def linda_status(self):
        timeout=None
        return self._send_and_wait(LindaOperate.STATUS, ["status"], timeout)

    def linda_reboot(self):
        timeout=None
        return self._send_and_wait(LindaOperate.REBOOT, ["reboot"], timeout)
        
    ########################

    def get_node_id(self):
        return self.NODE_ID

    def pub_notification(self, content, topic=NOTIFICATION_TOPIC, type="INFO"):
        '''
        type
            ERROR
            INFO
        {
            topic: 
            payload: {
                content:
            }
        }
        '''
        node_id = self.NODE_ID
        payload = self.message_template()["payload"]
        payload["type"] = type
        payload["content"] = content
        self.publish_payload(payload, topic)

    def pub_html_notification(self,
                              html_content,
                              topic=NOTIFICATION_TOPIC,
                              type="INFO"):
        '''
        type
            ERROR
            INFO
        {
            topic: 
            payload: {
                content:
            }
        }
        '''
        node_id = self.NODE_ID
        payload = self.message_template()["payload"]
        payload["type"] = type
        payload["html"] = True
        # json 描述
        payload["content"] = html_content  # html
        self.publish_payload(payload, topic)

    def pub_device_connect_status(self):
        '''
        msg_type?or topic?
        different content
            device name
            node_id
            status: connect/disconnect
        '''
        pass

    def stdin_ask(self):
        '''
        https://jupyter-client.readthedocs.io/en/stable/messaging.html#messages-on-the-stdin-router-dealer-channel
        use future(set future)? or sync
            pub/sub channel
        a special topic or msg_type
            build in
        '''
        pass

    def pub_status(self, extension_statu_map):
        '''
        pub node status
        '''
        topic = NODES_STATUS_TOPIC
        payload = self.message_template()["payload"]
        payload["content"] = extension_statu_map
        self.publish_payload(payload, topic)

    def pub_extension_statu_change(self, node_name, statu):
        topic = NODE_STATU_CHANGE_TOPIC
        node_id = self.NODE_ID
        payload = self.message_template()["payload"]
        payload["node_name"] = node_name
        payload["content"] = statu
        self.publish_payload(payload, topic)

    def receive_loop_as_thread(self):
        threaded(self.receive_loop)()

    def message_handle(self, topic, payload):
        """
        Override this method with a custom adapter message processor for subscribed messages.
        :param topic: Message Topic string.
        :param payload: Message Data.

        all the sub message
        process handler

        default sub: [SCRATCH_TOPIC, NODES_OPERATE_TOPIC]
        """
        if SPEED_DEBUG:
            self.logger.debug(f"SPEED_DEBUG-message_handle: {time.time()}, topic:{topic}")
        if self.external_message_processor:
            # handle all sub messages
            # to handle websocket message
            self.external_message_processor(topic, payload)

        if topic == NODES_OPERATE_TOPIC:
            '''
            分布式: 主动停止 使用node_id
                extension也是在此关闭，因为extension也是一种node
            UI触发关闭命令
            '''
            command = payload.get('content')
            if command == 'stop':
                '''
                to stop node/extension
                '''
                # 暂不处理extension
                # payload.get("node_id") == self.NODE_ID to stop extension
                # f'eim/{payload.get("node_name")}' == self.NODE_ID to stop node (generate extension id)
                if payload.get("node_id") == self.NODE_ID or payload.get(
                        "node_id") == "all" or self._node_name_to_node_id(
                            payload.get("node_name")) == self.NODE_ID:
                    # self.logger.debug(f"node stop message: {payload}")
                    # self.logger.debug(f"node self.name: {self.name}")
                    self.logger.info(f"stop {self}")
                    self.exit_message_handle(topic, payload)
            return

        if topic in [SCRATCH_TOPIC]:
            '''
            x 接受来自scratch的消息
            v 接受所有订阅主题的消息
            插件业务类
            '''
            if payload.get("node_id") == self.NODE_ID:
                self.extension_message_handle(topic, payload)
                '''
                handlers = self.get_handlers(type="current_extension")
                for handler in handlers:
                    handler(topic, payload)
                '''
        
        if topic == LINDA_CLIENT:
            for (message_id, future) in self.linda_wait_futures:
                if message_id == payload.get("message_id"):
                    future.set_result(payload["tuple"])
                    break

        if topic in [LINDA_CLIENT, LINDA_SERVER]:
            if hasattr(self, "_linda_message_handle"):
                getattr(self, "_linda_message_handle")(topic, payload)
            
            # todo : 如果存在 _linda_message_handle，则调用，所有的都收
            
            

    def terminate(self, stop_cmd_message_id=None):
        if self._running:
            self.logger.info(f"stopped {self.NODE_ID}")
            self.pub_notification(f"停止 {self.NODE_ID}")  # 会通知给 UI
            if stop_cmd_message_id:
                self.send_reply(stop_cmd_message_id)
            # super().terminate()
            # 释放 future
            # for (message_id, future) in self.linda_wait_futures:
            for (message_id, f) in self.linda_wait_futures:
                if not f.done():
                    f.set_exception(NodeTerminateError("terminate"))
                    # f.set_result(Exception("terminate"))
                    # f.set_result("terminate")
                    # time.sleep(0.1)
            
            self.clean_up()

    def is_connected(self, timeout=0.1):
        # ping set timeout
        _tuple = ["%%ping", "ping"]
        try:
            res = self._send_and_wait(LindaOperate.OUT, _tuple, timeout=timeout)
            return True
        except LindaTimeoutError as e:
            return False

class JupyterNode(AdapterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SimpleNode(JupyterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def simple_publish(self, content):
        message = {"payload": {"content": ""}}
        message["payload"]["content"] = content
        self.publish(message)
