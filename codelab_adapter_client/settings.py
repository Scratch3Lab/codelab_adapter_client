# import from user settings
import os
import pathlib
import sys
import time
from time import gmtime, strftime
import platform

from loguru import logger

ADAPTER_HOME_PATH = os.getenv('ADAPTER_HOME_PATH')
CN_PIP_MIRRORS_HOST = "https://pypi.tuna.tsinghua.edu.cn/simple"
PYTHON3_PATH = None

def is_in_china():
    # current time zone
    c_zone = strftime("%z", gmtime()) # time.strftime('%Z', time.localtime()) # fuck windows 🖕️
    if c_zone == "+0800":
        return True


# CN_PIP MIRRORS
USE_CN_PIP_MIRRORS = False  # may be overwriten by user settings
if is_in_china():
    USE_CN_PIP_MIRRORS = True

if ADAPTER_HOME_PATH:
    ADAPTER_HOME = pathlib.Path(ADAPTER_HOME_PATH)
else:
    ADAPTER_HOME = pathlib.Path.home() / "codelab_adapter"

sys.path.insert(1, str(ADAPTER_HOME))

# loop time
ZMQ_LOOP_TIME = 0.02

try:
    from user_settings import *
except Exception as e:
    # not found
    logger.error(str(e))
