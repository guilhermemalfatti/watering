import json
from plugins.plugin_interface import PluginInterface
from shared.const import TOPIC_DEVICE_PONG, TOPIC_DEVICE_PING, WateringAction
from pubsub import PubSubService


class Pong(PluginInterface):
    # Callback when the subscribed topic receives a message
    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        print("Received message from topic '{}': {}".format(topic, payload))
        try:
            pubsub_service = PubSubService()
            pubsub_service.publish(
                TOPIC_DEVICE_PONG, json.dumps({"status": "on"}))
            print("Pong sent")
        except json.JSONDecodeError as e:
            print("Failed to decode JSON payload: {}".format(e))

    def run(self):
        pubsub_service = PubSubService()
        pubsub_service.subscribe(TOPIC_DEVICE_PING,
                                 self.on_message_received)
