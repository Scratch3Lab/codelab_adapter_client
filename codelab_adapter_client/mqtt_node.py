# https://github.com/eclipse/paho.mqtt.python
import paho.mqtt.client as mqtt
from loguru import logger
import time


class MQTT_Node:
    def __init__(self, **kwargs):
        # super().__init__(**kwargs)
        # mqtt settings
        self.address = kwargs.get("address", "mqtt.longan.link")
        self.port = kwargs.get("port", 1883)
        self.username = kwargs.get("port", "guest")
        self.password = kwargs.get("port", "test")

        self.sub_topics = kwargs.get("sub_topics", ["/scratch3"])
        # mqtt client
        self.client = mqtt.Client()
        self.client.on_connect = kwargs.get("on_connect", self._on_connect)
        self.client.on_message = kwargs.get("on_message", self.on_message)
        self.client.on_disconnect = kwargs.get("on_message", self._on_disconnect)
        self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.address, self.port, 60)
        self.client.loop_start()  # as thread

    def _on_connect(self, client, userdata, flags, rc):
        logger.info(
            "MQTT Gateway Connected to MQTT {}:{} with result code {}.".format(
                self.address, self.port, str(rc)))
        # when mqtt is connected to subscribe to mqtt topics
        if self.sub_topics:
            for topic in self.sub_topics:
                client.subscribe(topic)

    def _on_disconnect(self, client, userdata, flags, rc):
        logger.warning('disconnect')

    def on_message(self, client, userdata, msg):
        '''
        msg.topic string
        msg.payload bytes
        '''
        logger.debug(f"topic->{msg.topic} ;payload-> {msg.payload}")
        # import IPython;IPython.embed()
        # todo reply mqtt
        # logger.debug((client, userdata, msg))

    # client.publish(topic, payload=None, qos=0, retain=False, properties=None)
    def publish(self, topic, payload, **kwargs):
        '''
        原始结构 raw_payload bytes
        '''
        self.client.publish(topic, payload=payload, **kwargs)


class EIM_MQTT_Node:
    '''
    EIM over MQTT
    '''
    pass


if __name__ == "__main__":
    node = MQTT_Node()
    while True:
        time.sleep(1)