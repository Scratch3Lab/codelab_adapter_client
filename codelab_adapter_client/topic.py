# adapter data
ADAPTER_TOPIC = "adapter/extensions/data"  # 来自插件的消息，topic

# scratch command
SCRATCH_TOPIC = "scratch/extensions/command"
# JUPYTER_TOPIC = "from_jupyter/extensions"

# core
# EXTENSIONS_OPERATE_TOPIC由manage订阅，node自治
EXTENSIONS_OPERATE_TOPIC = "core/extensions/operate" # 区分extensions和node(server)
NODES_OPERATE_TOPIC = "core/nodes/operate"
EXTENSIONS_STATUS_TOPIC = "core/extensions/status"
EXTENSIONS_STATUS_TRIGGER_TOPIC = "core/extensions/status/trigger"
EXTENSION_STATU_CHANGE_TOPIC = "core/extension/statu/change"
NOTIFICATION_TOPIC = "core/notification"

# ble
ADAPTER_BLE_TOPIC = "adapter/ble"
SCRATCH_BLE_TOPIC = "scratch/ble"

# mqtt
TO_MQTT_TOPIC = "to_mqtt"
FROM_MQTT_TOPIC = "from_mqtt"

# jupyter

# Home Assistant
FROM_HA_TOPIC = "from_HA"
TO_HA_TOPIC = "to_HA"

# websocket(socketio)
# Home Assistant
FROM_WEBSOCKET_TOPIC = "from_websocket"
TO_WEBSOCKET_TOPIC = "to_websocket"