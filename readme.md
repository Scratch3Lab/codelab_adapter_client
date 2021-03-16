# codelab_adapter_client
Python Client of [CodeLab Adapter](https://adapter.codelab.club/) v3.

# Install
```bash
# Python >= 3.6
pip install codelab_adapter_client 
```

# Usage
```python
from codelab_adapter_client import AdapterNode
```

# example
[extension_eim.py](https://github.com/wwj718/codelab_adapter_client/blob/master/examples/extension_eim.py)

# tools(for debugging)
```
codelab-message-monitor # subscribes to all messages and print both topic and payload.
codelab-message-trigger # pub the message in json file(`/tmp/message.json`).
codelab-message-pub -j '{"topic":"eim/test","payload":{"content":"test contenst"}}'
```

`/tmp/message.json`:

```json
{
  "topic": "adapter_core/exts/operate",
  "payload": { "content": "start", "node_name": "extension_eim" }
}
```

# FAQ
## 在 Adapter jupyterlab 中升级 codelab_adapter_client
```py
import pip
pip.main(['install', 'https://github.com/CodeLabClub/codelab_adapter_client_python/archive/master.zip'])
```

## EIM message
与 Scratch EIM 积木配合使用

```
from codelab_adapter_client.message import receive_message, send_message
```