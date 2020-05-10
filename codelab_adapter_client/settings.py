# import from user settings
import os
import pathlib
import sys
import time

from loguru import logger

ADAPTER_HOME_PATH = os.getenv('ADAPTER_HOME_PATH')
CN_PIP_MIRRORS_HOST = "mirrors.aliyun.com"


def is_in_china():
    # current time zone
    c_zone = time.strftime('%Z', time.localtime())
    if c_zone == "CST":
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

try:
    from user_settings import *
except Exception as e:
    # not found
    logger.error(str(e))
