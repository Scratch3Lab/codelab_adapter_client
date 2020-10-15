import argparse
import signal
import sys
import zmq
import json

from codelab_adapter_client.topic import ADAPTER_TOPIC, SCRATCH_TOPIC, NOTIFICATION_TOPIC, EXTS_OPERATE_TOPIC
from codelab_adapter_client.utils import threaded
from codelab_adapter_client import AdapterNode

# todo 交互式输入工具


class Pub(AdapterNode):
    """
    This class pub messages on the hub.

    help:   
        codelab-message-pub -h
    usage:
        codelab-message-pub -t hello_topic
        codelab-message-pub -d eim/node_test
        codelab-message-pub -c hello_content
        codelab-message-pub -j '{"payload":{"content":"test contenst", "node_id": "eim"}}'
    """

    def __init__(self,
                 codelab_adapter_ip_address=None,
                 subscriber_port='16103',
                 publisher_port='16130',
                 name=None,
                 ):
        super().__init__(
            name=name,
            codelab_adapter_ip_address=codelab_adapter_ip_address,
            subscriber_port=subscriber_port,
            publisher_port=publisher_port,
            start_cmd_message_id = -1 # 为了防止命令行参数被提前解析，丑陋的补丁
            )

        self.set_subscriber_topic('')


def pub():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        dest="codelab_adapter_ip_address",
        default="None",
        help="None or IP address used by CodeLab Adapter")
    parser.add_argument(
        "-n", dest="name", default="Pub", help="Set name in banner")
    parser.add_argument(
        "-p", dest="publisher_port", default='16130', help="Publisher IP port")
    parser.add_argument(
        "-s",
        dest="subscriber_port",
        default='16103',
        help="Subscriber IP port")
    parser.add_argument(
        "-t", dest="topic", default=ADAPTER_TOPIC, help="message topic")
    parser.add_argument(
        "-d", dest="node_id", default='eim', help="node id")
    parser.add_argument(
        "-c", dest="content", default='hi', help="payload['content']")
    parser.add_argument(
        "-j",
        dest="json_message",
        default='',
        help="json message(with topic and payload)")

    args = parser.parse_args()
    kw_options = {}

    if args.codelab_adapter_ip_address != 'None':
        kw_options[
            'codelab_adapter_ip_address'] = args.codelab_adapter_ip_address

    kw_options['name'] = args.name
    kw_options['publisher_port'] = args.publisher_port
    kw_options['subscriber_port'] = args.subscriber_port

    my_pub = Pub(**kw_options)

    if args.json_message:
        message = json.loads(args.json_message)
        topic = message["topic"]
        payload = message["payload"]
    else:
        payload = my_pub.message_template()["payload"]
        payload["content"] = args.content
        
    topic = args.topic
    if payload.get("node_id", None):
        payload["node_id"] = args.node_id

    my_pub.publish_payload(payload, topic)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    '''
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_pub.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    '''


if __name__ == '__main__':
    pub()
