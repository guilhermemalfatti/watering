from plugins.plugin_interface import PluginInterface
import time
from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import threading
import time
import json
import gpiozero
from shared.const import AWS_IOT_ENDPOINT, CERTIFICATE_PATH, CLIENT_ID,  PRIVATE_KEY_PATH, PUMP_GPIO, ROOT_CA_PATH, TOPIC_WATERING_SMALL, WateringAction
import RPi.GPIO as GPIO

received_all_event = threading.Event()


class SmallPlantsWatering(PluginInterface):

    def run_pump(self, seconds):
        print(f"Running for {seconds} seconds")
        # pumpRelay = gpiozero.OutputDevice(PUMP_GPIO, active_high=False,
        #                                   initial_value=False)

        # pumpRelay.on()
        # time.sleep(seconds)
        # pumpRelay.off()
        GPIO.setwarnings(False)    # Ignore warning for now
        GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
        GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)
        print("Pump off")

    def turn_off_pump(self, ):
        print("Turning off pump")
        pumpRelay = gpiozero.OutputDevice(PUMP_GPIO, active_high=False,
                                          initial_value=False)

        pumpRelay.off()

    # Callback when the subscribed topic receives a message
    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        print("Received message from topic '{}': {}".format(topic, payload))
        try:
            message = json.loads(payload)
            action = message["status"]
            match action:
                case WateringAction.ON.value:
                    self.run_pump(message['seconds'])
                case WateringAction.OFF.value:
                    self.turn_off_pump()
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

        # Subscribe
        print("Subscribing to topic '{}'...".format(TOPIC_WATERING_SMALL))
        subscribe_future, packet_id = mqtt_connection.subscribe(
            topic=TOPIC_WATERING_SMALL,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self.on_message_received)

        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(str(subscribe_result['qos'])))

        # Wait for all messages to be received.
        if not received_all_event.is_set():
            print("Waiting for all messages to be received...")

        # TODO this is just to keep it running forever, we might want implement something to be based on the message we stop the servie
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
