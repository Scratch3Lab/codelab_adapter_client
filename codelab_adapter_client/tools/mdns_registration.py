""" Example of announcing a service (in this case, a fake HTTP server) """

import argparse
import logging
import socket
from time import sleep
import uuid

from zeroconf import IPVersion, ServiceInfo, Zeroconf
from codelab_adapter_client.utils import get_local_ip

# if __name__ == '__main__':
def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument("--name", dest="name", default=None,
                        help="mdns service name")
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument('--v6', action='store_true')
    version_group.add_argument('--v6-only', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    if args.v6:
        ip_version = IPVersion.All
    elif args.v6_only:
        ip_version = IPVersion.V6Only
    else:
        ip_version = IPVersion.V4Only

    properties = {'who': 'codelab'}  # 详细信息

    name = args.name if args.name else uuid.uuid4().hex[:8]

    service_type = "_http._tcp.local."
    service_name = f"{name}._http._tcp.local."
    server = f"{name}.local." 
    port = 12358
    info = ServiceInfo(
        service_type,
        service_name,
        addresses=[socket.inet_aton(get_local_ip())],
        port=port,
        properties=properties,
        server=server,
    )
    print(info)
    zeroconf = Zeroconf(ip_version=ip_version)
    print("Registration of a service, press Ctrl-C to exit...")
    zeroconf.register_service(info)
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()