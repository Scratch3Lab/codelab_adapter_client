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
