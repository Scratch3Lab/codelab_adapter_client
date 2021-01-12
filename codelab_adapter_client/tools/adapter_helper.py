# adapter helper
from pprint import pprint
# show adapter home path
from codelab_adapter_client.config import settings
from codelab_adapter_client.utils import open_path_in_system_file_manager

def adapter_helper():
    pprint(f"adapter home: {settings.ADAPTER_HOME_PATH}") # open it
    # open_path_in_system_file_manager(ADAPTER_HOME)

def list_settings():
    pprint(settings.as_dict())
    # print()
    # open_path_in_system_file_manager(ADAPTER_HOME)