from plugins.plugin_interface import PluginInterface
from time import sleep
import time
from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import threading
import json
import gpiozero
from shared.const import PUMP_GPIO, TOPIC_WATERING_STOPED, TOPIC_WATERING_STOP, TOPIC_WATERING_SMALL, TOPIC_DEVICE_LAST_WATERED, WateringAction
import RPi.GPIO as GPIO

from pubsub import PubSubService

received_all_event = threading.Event()


class SmallPlantsWatering(PluginInterface):

    def __init__(self):
        self.is_watering = False

    def run_pump(self, seconds):
        self.is_watering = True
        GPIO.setwarnings(False)    # Ignore warning for now
        GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
        GPIO.setup(PUMP_GPIO, GPIO.OUT, initial=True)

        print(f"Running for {seconds} seconds")
        GPIO.output(PUMP_GPIO, False)  # Turn on

        sleep(seconds)

        self.turn_off_pump()

        sleep(1)

        pubsub_service = PubSubService()
        pubsub_service.publish(TOPIC_DEVICE_LAST_WATERED, json.dumps(
            {"timestamp": time.strftime('%Y-%m-%d %H:%M:%S')}))

    def turn_off_pump(self):
        if self.is_watering:
            print("Turning off pump")
            GPIO.output(PUMP_GPIO, True)
            self.is_watering = False

            pubsub_service = PubSubService()
            pubsub_service.publish(TOPIC_WATERING_STOPED, json.dumps(
                {"status": "off"}))
        else:
            print("Pump is not running, no need to turn off")

    # Callback when the subscribed topic receives a message
    def on_start_event(self, topic, payload, dup, qos, retain, **kwargs):
        print("Received message from topic '{}': {}".format(topic, payload))
        try:
            message = json.loads(payload)
            self.run_pump(message['seconds'])
        except json.JSONDecodeError as e:
            print("Failed to decode JSON payload: {}".format(e))

    def on_stop_event(self, topic, payload, dup, qos, retain, **kwargs):
        print("Received message from topic '{}': {}".format(topic, payload))
        try:
            self.turn_off_pump()
        except json.JSONDecodeError as e:
            print("Failed to decode JSON payload: {}".format(e))

    def run(self):
        pubsub_service = PubSubService()
        pubsub_service.subscribe(TOPIC_WATERING_SMALL,
                                 lambda *args, **kwargs: threading.Thread(target=self.on_start_event, args=args, kwargs=kwargs).start())

        pubsub_service.subscribe(TOPIC_WATERING_STOP,
                                 lambda *args, **kwargs: threading.Thread(target=self.on_stop_event, args=args, kwargs=kwargs).start())

        print("[plugin-small] waiting for a command!")
        received_all_event.wait()
        print("[plugin-small] stopping the service!")
