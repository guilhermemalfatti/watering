from plugins.plugin_interface import PluginInterface
import time
from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import threading
import time
import json

from shared.const import AWS_IOT_ENDPOINT, CERTIFICATE_PATH, CLIENT_ID, MQTT_TOPIC, PRIVATE_KEY_PATH, ROOT_CA_PATH, WateringAction

received_all_event = threading.Event()


class SmallPlantsWatering(PluginInterface):

    # Callback when the subscribed topic receives a message
    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        print("Received message from topic '{}': {}".format(topic, payload))
        try:
            message = json.loads(payload)
            action = message["status"]
            match action:
                case WateringAction.ON.value:
                    print(f"Running for {message['seconds']} seconds")
                case WateringAction.OFF.value:
                    print(f"Turning off")
                case _:
                    print(f"Unknown action: {action}")
        except json.JSONDecodeError as e:
            print("Failed to decode JSON payload: {}".format(e))

    def water(self):
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=AWS_IOT_ENDPOINT,
            port=None,
            cert_filepath=CERTIFICATE_PATH,
            pri_key_filepath=PRIVATE_KEY_PATH,
            ca_filepath=ROOT_CA_PATH,
            on_connection_interrupted=self.on_connection_interrupted,
            on_connection_resumed=self.on_connection_resumed,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=30,
            http_proxy_options=None,
            on_connection_success=self.on_connection_success,
            on_connection_failure=self.on_connection_failure,
            on_connection_closed=self.on_connection_closed)

        print(
            f"Connecting to {AWS_IOT_ENDPOINT} with client ID '{CLIENT_ID}'...")
        connect_future = mqtt_connection.connect()

        # Future.result() waits until a result is available
        connect_future.result()
        print("Connected!")

        message_topic = MQTT_TOPIC

        # Subscribe
        print("Subscribing to topic '{}'...".format(message_topic))
        subscribe_future, packet_id = mqtt_connection.subscribe(
            topic=message_topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self.on_message_received)

        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(str(subscribe_result['qos'])))

        # Wait for all messages to be received.
        # This waits forever if count was set to 0.
        if not received_all_event.is_set():
            print("Waiting for all messages to be received...")

        # TODO this is just to keep it riunning forever, we might want implement something to based the message we stop the servie
        while not received_all_event.is_set():
            print(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')} - [small] waiting for a command!", flush=True)
            time.sleep(5)

        received_all_event.wait()
        print("{} message(s) received.".format(received_count))

        # Disconnect
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")


# unzip connect_device_package.zip
