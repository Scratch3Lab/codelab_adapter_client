""" 
# https://github.com/jstasiak/python-zeroconf/blob/master/examples/browser.py

Example of browsing for a service.

The default is HTTP and HAP; use --find to search for all available services in the network

HAP（homekit accessory protocol(HAP)） 协议 是 apple 发布的用于 ios 手机作为controller, 去控制 accessory 的用于智能家居的一个通讯协议。有两种方式： ble 和IP.

HAP-python
"""

import argparse
import logging
import socket
from time import sleep
from typing import cast

from zeroconf import IPVersion, ServiceBrowser, ServiceStateChange, Zeroconf, ZeroconfServiceTypes


def on_service_state_change(
    zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange
) -> None:
    print("Service %s of type %s state changed: %s" % (name, service_type, state_change))

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        print("Info from zeroconf.get_service_info: %r" % (info))
        if info:
            addresses = ["%s:%d" % (socket.inet_ntoa(addr), cast(int, info.port)) for addr in info.addresses]
            print("  Addresses: %s" % ", ".join(addresses))
            print("  Weight: %d, priority: %d" % (info.weight, info.priority))
            print("  Server: %s" % (info.server,))
            if info.properties:
                print("  Properties are:")
                for key, value in info.properties.items():
                    print("    %s: %s" % (key, value))
            else:
                print("  No properties")
        else:
            print("  No info")
        print('\n')


# if __name__ == '__main__':
def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--find', action='store_true', help='Browse all available services')
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

    zeroconf = Zeroconf(ip_version=ip_version)

    services = ["_http._tcp.local.", "_hap._tcp.local."]
    if args.find:
        services = list(ZeroconfServiceTypes.find(zc=zeroconf))

    print("\nBrowsing %d service(s), press Ctrl-C to exit...\n" % len(services))
    browser = ServiceBrowser(zeroconf, services, handlers=[on_service_state_change])

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()