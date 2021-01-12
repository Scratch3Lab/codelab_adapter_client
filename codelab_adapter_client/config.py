import pathlib
import sys
from dynaconf import Dynaconf

def is_in_china():
    from time import gmtime, strftime
    # current time zone
    c_zone = strftime("%z", gmtime()) # time.strftime('%Z', time.localtime()) # fuck windows 🖕️
    if c_zone == "+0800":
        return True

# user_settings_file = '~/codelab_adapter/user_settings.toml'
ADAPTER_HOME = pathlib.Path.home() / "codelab_adapter"
user_settings_file = ADAPTER_HOME / 'user_settings.toml'

global_settings_file = ADAPTER_HOME / "global_settings.toml"

if global_settings_file.is_file():
    settings_files = [str(global_settings_file)]
else:
    settings_files = []

if user_settings_file.is_file():
    settings_files.append(str(user_settings_file))

settings = Dynaconf(
    envvar_prefix="CODELAB",
    # envvar_prefix False 将获取所有环境变量
    # envvar_prefix=False, # https://www.dynaconf.com/envvars/#custom-prefix
    # 'settings.py',
    # 'settings.toml'  '.secrets.toml'
    settings_files=settings_files, # todo ~/codelab_adapter/user_settings.py
) # 按顺序加载， .local

if not settings.get("ZMQ_LOOP_TIME"):
    # export CODELAB_ZMQ_LOOP_TIME = 0.01
    settings.ZMQ_LOOP_TIME = 0.02

if not settings.get("ADAPTER_HOME_PATH"):  # 环境
    settings.ADAPTER_HOME_PATH = str(pathlib.Path.home() / "codelab_adapter")

sys.path.insert(1, settings.ADAPTER_HOME_PATH)

# CN_PIP MIRRORS
if not settings.get("USE_CN_PIP_MIRRORS"):
    settings.USE_CN_PIP_MIRRORS = False  # may be overwriten by user settings
    if is_in_china():
        settings.USE_CN_PIP_MIRRORS = True
    
if not settings.get("CN_PIP_MIRRORS_HOST"):
    settings.CN_PIP_MIRRORS_HOST = "https://pypi.tuna.tsinghua.edu.cn/simple"

if not settings.get("PYTHON3_PATH"):
    PYTHON3_PATH = None

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load this files in the order.
