# work with https://adapter.codelab.club/extension_guide/microbit/
import time
from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.topic import ADAPTER_TOPIC, SCRATCH_TOPIC


class MicrobitNode(AdapterNode):
    '''
    send/recv microbit extension message
    duck like scratch
    '''

    def __init__(self):
        super().__init__(
            logger=logger,
            external_message_processor=self.external_message_processor)
        self.TOPIC = SCRATCH_TOPIC
        self.NODE_ID = "eim/usbMicrobit"
        self.set_subscriber_topic(ADAPTER_TOPIC)

    def microbit_event(self, data):
        pass

    def external_message_processor(self, topic, payload):
        # self.logger.info(f'the message payload from extention: {payload}')
        if topic == ADAPTER_TOPIC:
            node_id = payload["node_id"]
            if node_id == self.NODE_ID:
                content = payload["content"]
                self.microbit_event(content)

    def send_command(self,
                     content="display.show('hi', wait=True, loop=False)"):
        heart = "Image(\"07070:70707:70007:07070:00700\""  # show heart
        message = self.message_template()
        message['payload']['content'] = content
        self.publish(message)

    def run(self):
        while self._running:
            time.sleep(1)


if __name__ == "__main__":
    try:
        node = MicrobitNode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.