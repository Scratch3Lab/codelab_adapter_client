import functools
import threading
import time
import pathlib
from loguru import logger

def get_or_create_codelab_adapter_dir():
    dir = pathlib.Path.home() / "codelab_adapter"
    dir.mkdir(parents=True, exist_ok=True)
    return dir

def get_or_create_node_logger_dir():
    codelab_adapter_dir = get_or_create_codelab_adapter_dir()
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
    logger.add(debug_log, rotation="1 MB", level="DEBUG")
    logger.add(info_log, rotation="1 MB", level="INFO")
    logger.add(error_log, rotation="1 MB", level="ERROR")


def threaded(function):
    """
    https://github.com/malwaredllc/byob/blob/master/byob/core/util.py#L514

    Decorator for making a function threaded
    `Required`
    :param function:    function/method to run in a thread
    """

    @functools.wraps(function)
    def _threaded(*args, **kwargs):
        t = threading.Thread(
            target=function, args=args, kwargs=kwargs, name=time.time())
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