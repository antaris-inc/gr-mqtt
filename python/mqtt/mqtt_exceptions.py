class MQTTConnectionError(Exception):
    """Custom exception for MQTT connection failures."""
    pass

class MQTTDisconnectError(Exception):
    """Custom exception for MQTT disconnect failures."""
    pass