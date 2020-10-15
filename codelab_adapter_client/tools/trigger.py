import argparse
import signal
import sys
import zmq
import json

from codelab_adapter_client.topic import  ADAPTER_TOPIC, SCRATCH_TOPIC, NOTIFICATION_TOPIC, EXTS_OPERATE_TOPIC
from codelab_adapter_client.utils import threaded
from codelab_adapter_client import AdapterNode


# todo 交互式输入工具

class Trigger(AdapterNode):
    """
    This class subscribes to all messages on the hub and prints out both topic and payload.
    """

    def __init__(self, codelab_adapter_ip_address=None,
                 subscriber_port='16103', publisher_port='16130', name=None):
        super().__init__(
            name=name,
            codelab_adapter_ip_address=codelab_adapter_ip_address,
            subscriber_port=subscriber_port,
            publisher_port=publisher_port,
            start_cmd_message_id = -1
            )

        self.set_subscriber_topic('')
        self.run()
        try:
            self.receive_loop()
        except zmq.error.ZMQError:
            sys.exit()
        except KeyboardInterrupt:
            sys.exit()

    def message_handle(self, topic, payload):
        pass
        # print(topic, payload)
    
    @threaded
    def run(self):
        while self._running:
            # print(">>>self.publish({'topic':EXTS_OPERATE_TOPIC,'payload':{'content':'start', 'node_id':'extension_eim2'}})")
            code = input(">>>read json from /tmp/message.json (enter to run)")
            with open("/tmp/message.json") as f:
                message = json.loads(f.read())
            self.publish(message)

def trigger():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", dest="codelab_adapter_ip_address", default="None",
                        help="None or IP address used by CodeLab Adapter")
    parser.add_argument("-n", dest="name", default="Trigger", help="Set name in banner")
    parser.add_argument("-p", dest="publisher_port", default='16130',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='16103',
                        help="Subscriber IP port")

    args = parser.parse_args()
    kw_options = {}

    if args.codelab_adapter_ip_address != 'None':
        kw_options['codelab_adapter_ip_address'] = args.codelab_adapter_ip_address

    kw_options['name'] = args.name

    kw_options['publisher_port'] = args.publisher_port
    kw_options['subscriber_port'] = args.subscriber_port

    my_trigger = Trigger(**kw_options)
    # my_monitor.start()

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_trigger.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    trigger()
