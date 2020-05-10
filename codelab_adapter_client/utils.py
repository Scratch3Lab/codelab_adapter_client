import functools
import os
import pathlib
import platform
import subprocess
import threading
import time
import platform
from codelab_adapter_client.settings import PYTHON3_PATH, CN_PIP_MIRRORS_HOST, USE_CN_PIP_MIRRORS

from loguru import logger


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
    if PYTHON3_PATH:
        # 允许用户覆盖PYTHON3_PATH
        logger.info(
            f"local python3_path-> {PYTHON3_PATH}, overwrite by user settings")
        return PYTHON3_PATH
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
    if USE_CN_PIP_MIRRORS:
        return f"-i {CN_PIP_MIRRORS_HOST}"  # settings
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