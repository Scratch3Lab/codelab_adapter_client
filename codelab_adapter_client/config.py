import pathlib
import sys
import platform
import pkg_resources

from dynaconf import Dynaconf


def is_win():
    if platform.system() == "Windows":
        return True


def is_mac():
    if platform.system() == "Darwin":
        # which python3
        # 不如用PATH python
        return True


def is_linux():
    if platform.system() == "Linux":
        return True


def look_up_root():
    """
    adapter home root dir
    """
    python_path = sys.executable  # str
    if is_mac():
        # app、 app_packages、 Support(mac)/python(win)
        resources_dir = pathlib.Path(python_path).parents[2]
    if is_win():
        resources_dir = pathlib.Path(python_path).parents[1]
    if is_linux():
        # 作为 root
        resources_dir = pathlib.Path.home()
    return resources_dir

def is_in_china():
    from time import gmtime, strftime
    # current time zone
    c_zone = strftime("%z", gmtime()) # time.strftime('%Z', time.localtime()) # fuck windows 🖕️
    if c_zone == "+0800":
        return True


ADAPTER_HOME_DIR_NAME = "adapter_home"
ROOT = look_up_root()
CODELAB_ADAPTER_DIR = ROOT / ADAPTER_HOME_DIR_NAME
ADAPTER_HOME = CODELAB_ADAPTER_DIR  # 如果不存在， 就不存在

user_settings_file = ADAPTER_HOME / 'user_settings.toml'

global_settings_file = ADAPTER_HOME / "global_settings.toml"

if global_settings_file.is_file():
    settings_files = [str(global_settings_file)]
else:
    settings_files = []

if user_settings_file.is_file():
    settings_files.append(str(user_settings_file))
else:
    print("未找到 user_settings_file")
    path = pathlib.Path(pkg_resources.resource_filename('codelab_adapter_client', f"data/user_settings.toml"))
    # 使用内置的
    print("使用 codelab_adapter_client 内置的 data/user_settings.toml")
    settings_files.append(str(path))

# 内置的配置，最弱

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
    settings.ADAPTER_HOME_PATH = str(CODELAB_ADAPTER_DIR)

sys.path.insert(1, settings.ADAPTER_HOME_PATH)

# CN_PIP MIRRORS
if not settings.get("USE_CN_PIP_MIRRORS"):
    settings.USE_CN_PIP_MIRRORS = False  # may be overwriten by user settings
    if is_in_china():
        settings.USE_CN_PIP_MIRRORS = True
    
if not settings.get("CN_PIP_MIRRORS_HOST"):
    settings.CN_PIP_MIRRORS_HOST = "https://pypi.tuna.tsinghua.edu.cn/simple"

if not settings.get("PYTHON3_PATH"):
    settings.PYTHON3_PATH = None

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load this files in the order.
if not settings.get("NODE_LOG_PATH"):
    settings.NODE_LOG_PATH = ADAPTER_HOME / "node_log"


# 获取TOKEN
def _get_adapter_home_token(codelab_adapter_dir):
    '''
    不同进程可以共享TOKEN，jupyter对port的操作类似
    '''
    token_file = pathlib.Path(codelab_adapter_dir) / '.token'
    if token_file.exists():
        with open(token_file) as f:
            TOKEN = f.read()
            return TOKEN

if not settings.get("TOKEN"):
    adapter_home_token = _get_adapter_home_token(settings.ADAPTER_HOME_PATH)
    if adapter_home_token:
        settings.TOKEN = adapter_home_token
