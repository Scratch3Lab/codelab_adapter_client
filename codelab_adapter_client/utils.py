import functools
import os
import pathlib
import platform
import subprocess
import sys
import threading
import time
import urllib
import urllib.request
import re
import base64
import socket
from enum import Enum

from loguru import logger

import uflash
from codelab_adapter_client.config import settings

def get_adapter_home_path():
    dir = pathlib.Path.home() / "codelab_adapter"
    # dir.mkdir(parents=True, exist_ok=True)
    return dir


def get_or_create_node_logger_dir():
    codelab_adapter_dir = get_adapter_home_path()
    dir = codelab_adapter_dir / "node_log"
    dir.mkdir(parents=True, exist_ok=True)
    return dir


def setup_loguru_logger():
    # 风险: 可能与adapter logger冲突， 同时读写文件
    # 日志由node自行处理
    node_logger_dir = get_or_create_node_logger_dir()
    debug_log = str(node_logger_dir / "debug.log")
    info_log = str(node_logger_dir / "info.log")
    error_log = str(node_logger_dir / "error.log")
    logger.add(debug_log, rotation="1 MB", retention="30 days", level="DEBUG")
    logger.add(info_log, rotation="1 MB", retention="30 days", level="INFO")
    logger.add(error_log, rotation="1 MB", retention="30 days", level="ERROR")


def get_python3_path():
    # todo 区分作为普通代码运行和作为冻结代码运行
    if not getattr(sys, 'frozen', False):
        # 普通模式 node
        return str(sys.executable)

    if settings.PYTHON3_PATH:
        # 允许用户覆盖settings.PYTHON3_PATH
        logger.info(
            f"local python3_path-> {settings.PYTHON3_PATH}, overwrite by user settings")
        return settings.PYTHON3_PATH
    # If it is not working,  Please replace python3_path with your local python3 path. shell: which python3
    if (platform.system() == "Darwin"):
        # which python3
        # 不如用PATH python
        path = "/usr/local/bin/python3"  # default
    if platform.system() == "Windows":
        path = "python"
    if platform.system() == "Linux":
        path = "/usr/bin/python3"
    logger.info(f"local python3_path-> {path}")
    return path


def threaded(function):
    """
    https://github.com/malwaredllc/byob/blob/master/byob/core/util.py#L514

    Decorator for making a function threaded
    `Required`
    :param function:    function/method to run in a thread
    """
    @functools.wraps(function)
    def _threaded(*args, **kwargs):
        t = threading.Thread(target=function,
                             args=args,
                             kwargs=kwargs,
                             name=time.time())
        t.daemon = True  # exit with the parent thread
        t.start()
        return t

    return _threaded


class TokenBucket:
    """An implementation of the token bucket algorithm.
    https://blog.just4fun.site/post/%E5%B0%91%E5%84%BF%E7%BC%96%E7%A8%8B/scratch-extension-token-bucket/#python%E5%AE%9E%E7%8E%B0
    
    >>> bucket = TokenBucket(80, 0.5)
    >>> print bucket.consume(10)
    True
    >>> print bucket.consume(90)
    False
    """
    def __init__(self, tokens, fill_rate):
        """tokens is the total tokens in the bucket. fill_rate is the
        rate in tokens/second that the bucket will be refilled."""
        self.capacity = float(tokens)
        self._tokens = float(tokens)
        self.fill_rate = float(fill_rate)
        self.timestamp = time.time()

    def consume(self, tokens):
        """Consume tokens from the bucket. Returns True if there were
        sufficient tokens otherwise False."""
        if tokens <= self.tokens:
            self._tokens -= tokens
        else:
            return False
        return True

    def get_tokens(self):
        if self._tokens < self.capacity:
            now = time.time()
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)
            self.timestamp = now
        return self._tokens

    tokens = property(get_tokens)


def subprocess_args(include_stdout=True):
    '''
    only Windows
    '''
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        env = os.environ
    else:
        si = None
        env = None

    ret = {}
    ret.update({
        'stdin': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'startupinfo': si,
        'env': env
    })
    return ret


def get_pip_mirrors():
    if settings.USE_CN_PIP_MIRRORS:
        return f"-i {settings.CN_PIP_MIRRORS_HOST}"  # settings
    else:
        return ""


def install_requirement(requirement, use_cn_mirrors=True):
    # adapter_home_path = get_or_create_codelab_adapter_dir()
    python_path = get_python3_path()
    pip_mirrors = get_pip_mirrors()  # maybe blank
    install_cmd = f'{python_path} -m pip install {" ".join(requirement)} {pip_mirrors} --upgrade'
    logger.debug(f"install_cmd -> {install_cmd}")
    output = subprocess.call(
        install_cmd,
        shell=True,
    )
    return output


def is_win():
    if platform.system() == "Windows":
        return True


def is_mac():
    if (platform.system() == "Darwin"):
        # which python3
        # 不如用PATH python
        return True


def is_linux():
    if platform.system() == "Linux":
        return True


# https://github.com/thonny/thonny/blob/master/thonny/ui_utils.py#L1764
def open_path_in_system_file_manager(path):
    if platform.system() == "Darwin":
        # http://stackoverflow.com/a/3520693/261181
        # -R doesn't allow showing hidden folders
        cmd = "open"
    if platform.system() == "Linux":
        cmd = "xdg-open"
    if platform.system() == "Windows":
        cmd = "explorer"
    subprocess.Popen([cmd, str(path)])
    return [cmd, str(path)]


def run_monitor(monitor_func, codelab_adapter_ip_address=None):
    from codelab_adapter_client.simple_node import EimMonitorNode
    logger.debug("waiting for a message...")
    try:
        node = EimMonitorNode(monitor_func, codelab_adapter_ip_address=codelab_adapter_ip_address, start_cmd_message_id=-1)
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.


def send_simple_message(content):
    import ssl
    # https eim send, python3
    # 阻塞问题 频率消息 http连接数？
    # 中文有问题
    url = f"https://codelab-adapter.codelab.club:12358/api/message/eim"
    data = {"message": content}
    url_values = urllib.parse.urlencode(data)
    full_url = url + '?' + url_values
    with urllib.request.urlopen(full_url, context=ssl.SSLContext()) as response:
        # html = response.read()
        return "success!"
    
def save_base64_to_image(src, name):
    """
    ref: https://blog.csdn.net/mouday/article/details/93489508
    解码图片
        eg:
            src="data:image/gif;base64,xxx" # 粘贴到在浏览器地址栏中可以直接显示
    :return: str 保存到本地的文件名
    """

    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src,
                       re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")
    else:
        raise Exception("Do not parse!")

    img = base64.urlsafe_b64decode(data)

    filename = "{}.{}".format(name, ext)
    with open(filename, "wb") as f:
        f.write(img)
    # do something with the image...
    return filename

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # 114.114.114.114
        ip = s.getsockname()[0]
        return ip
    except Exception as e:
        str(e)

class LindaTimeoutError(Exception):
    pass

class NodeTerminateError(Exception):
    pass

class LindaOperate(Enum):
    OUT = "out"
    IN = "in"
    INP = "inp"
    RD = "rd"
    RDP = "rdp"
    # helper
    DUMP = "dump"
    STATUS = "status"
    REBOOT = "reboot"

    