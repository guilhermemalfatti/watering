from plugins.plugin_interface import PluginInterface
import time
from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import threading
import time
import json
import gpiozero
from shared.const import PUMP_GPIO, TOPIC_WATERING_SMALL, TOPIC_DEVICE_LAST_WATERED, WateringAction
import RPi.GPIO as GPIO

from pubsub import PubSubService

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
        pubsub_service = PubSubService()
        pubsub_service.publish(TOPIC_DEVICE_LAST_WATERED, json.dumps(
            {"timestamp": time.strftime('%Y-%m-%d %H:%M:%S')}))

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

    def run(self):
        pubsub_service = PubSubService()
        pubsub_service.subscribe(TOPIC_WATERING_SMALL,
                                 self.on_message_received)
        # TODO this is just to keep it running forever, we might want implement something to be based on the message we stop the servie
        while not received_all_event.is_set():
            print(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')} - [small] waiting for a command!", flush=True)
            time.sleep(5)

        received_all_event.wait()


# unzip connect_device_package.zip
