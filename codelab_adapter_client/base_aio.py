import zmq
import zmq.asyncio
import time
import logging
import sys
import msgpack
from abc import ABCMeta, abstractmethod
from pathlib import Path
import asyncio

from codelab_adapter_client.topic import ADAPTER_TOPIC, SCRATCH_TOPIC, NOTIFICATION_TOPIC, EXTENSIONS_OPERATE_TOPIC
from codelab_adapter_client.utils import threaded

logger = logging.getLogger(__name__)


class MessageNodeAio(metaclass=ABCMeta):
    def __init__(
            self,
            name='',
            logger=logger,
            codelab_adapter_ip_address=None,
            subscriber_port='16103',
            publisher_port='16130',
            subscriber_list=None,
            loop_time=0.1,
            connect_time=0.3,
            external_message_processor=None,
            receive_loop_idle_addition=None,
            event_loop=None,
    ):
        '''
        :param codelab_adapter_ip_address: Adapter IP Address -
                                      default: 127.0.0.1
        :param subscriber_port: codelab_adapter subscriber port.
        :param publisher_port: codelab_adapter publisher port.
        :param loop_time: Receive loop sleep time.
        :param connect_time: Allow the node to connect to adapter
        '''
        self._running = True  # use it to receive_loop
        self.logger = logger
        if name:
            self.name = name
        else:
            self.name = type(self).__name__
        self.subscriber_list = subscriber_list
        self.receive_loop_idle_addition = receive_loop_idle_addition
        self.external_message_processor = external_message_processor
        self.connect_time = connect_time

        if codelab_adapter_ip_address:
            self.codelab_adapter_ip_address = codelab_adapter_ip_address
        else:
            # check for a running CodeLab Adapter
            # determine this computer's IP address
            self.codelab_adapter_ip_address = '127.0.0.1'

        self.subscriber_port = subscriber_port
        self.publisher_port = publisher_port
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

        if event_loop:
            self.event_loop = event_loop
        else:
            self.event_loop = asyncio.get_event_loop()

    def __str__(self):
        return self.name

    def get_publisher(self):
        return self.publisher

    async def set_subscriber_topic(self, topic):
        """
        This method sets a subscriber topic.
        You can subscribe to multiple topics by calling this method for
        each topic.
        :param topic: A topic string
        """

        if not type(topic) is str:
            raise TypeError('Subscriber topic must be string')

        self.subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode())

    async def pack(self, data):
        return msgpack.packb(data, use_bin_type=True)

    async def unpack(self, data):
        return msgpack.unpackb(data, raw=False)

    async def publish_payload(self, payload, topic=''):
        """
        This method will publish a  payload and its associated topic
        :param payload: Protocol message to be published
        :param topic: A string value
        """

        # make sure the topic is a string
        if not type(topic) is str:
            raise TypeError('Publish topic must be string', 'topic')

        message = await self.pack(payload)

        pub_envelope = topic.encode()
        await self.publisher.send_multipart([pub_envelope, message])

    async def receive_loop(self):
        """
        This is the receive loop for adapter messages.
        This method may be overwritten to meet the needs
        of the application before handling received messages.
        """
        # 放在init 可能会有线程问题
        # establish the zeromq sub and pub sockets and connect to the adapter
        self.context = zmq.asyncio.Context()  # zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        connect_string = "tcp://" + self.codelab_adapter_ip_address + ':' + self.subscriber_port
        self.subscriber.connect(connect_string)

        self.publisher = self.context.socket(zmq.PUB)
        connect_string = "tcp://" + self.codelab_adapter_ip_address + ':' + self.publisher_port
        self.publisher.connect(connect_string)

        if self.subscriber_list:
            for topic in self.subscriber_list:
                await self.set_subscriber_topic(topic)

        while self._running:
            data = await self.subscriber.recv_multipart()
            topic = data[0].decode()
            payload = await self.unpack(data[1])
            await self.message_handle(topic, payload)

    async def start_the_receive_loop(self):
        self.receive_loop_task = self.event_loop.create_task(
            self.receive_loop())

    async def message_handle(self, topic, payload):
        """
        Override this method with a custom adapter message processor for subscribed messages.
        :param topic: Message Topic string.
        :param payload: Message Data.
        """
        print('this method should be overwritten in the child class')

    # noinspection PyUnresolvedReferences

    async def clean_up(self):
        """
        Clean up before exiting.
        """
        self._running = False
        await self.publisher.close()
        await self.subscriber.close()
        await self.context.term()


class AdapterNodeAio(MessageNodeAio):
    '''
    CodeLab Adapter AdapterNodeAio
    '''

    def __init__(self, *args, **kwargs):
        '''
        :param codelab_adapter_ip_address: Adapter IP Address -
                                      default: 127.0.0.1
        :param subscriber_port: codelab_adapter subscriber port.
        :param publisher_port: codelab_adapter publisher port.
        :param loop_time: Receive loop sleep time.
        :param connect_time: Allow the node to connect to adapter
        '''
        super().__init__(*args, **kwargs)

        self.ADAPTER_TOPIC = ADAPTER_TOPIC  # message topic: the message from adapter
        self.SCRATCH_TOPIC = SCRATCH_TOPIC  # message topic: the message from scratch
        if not hasattr(self, 'EXTENSION_ID'):
            self.EXTENSION_ID = "eim"