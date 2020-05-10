# adapter helper

# show adapter home path
from codelab_adapter_client.settings import ADAPTER_HOME
from codelab_adapter_client.utils import open_path_in_system_file_manager

def adapter_helper():
    print(f"adapter home: {ADAPTER_HOME}") # open it
    # open_path_in_system_file_manager(ADAPTER_HOME)