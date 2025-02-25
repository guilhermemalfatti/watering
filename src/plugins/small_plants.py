from plugins.plugin_interface import PluginInterface
from time import sleep
import time
import threading
import json
from shared.const import PUMP_GPIO, TOPIC_DEVICE_LAST_WATERED_GET, TOPIC_WATERING_STOPED, TOPIC_WATERING_STOP, TOPIC_WATERING_SMALL, TOPIC_DEVICE_LAST_WATERED
import RPi.GPIO as GPIO
from pubsub import PubSubService
import logging

received_all_event = threading.Event()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SmallPlantsWatering(PluginInterface):

    def __init__(self):
        self.is_watering = False
        self.lastWatered = None

    def run_pump(self, seconds):
        self.is_watering = True
        GPIO.setwarnings(False)    # Ignore warning for now
        GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
        GPIO.setup(PUMP_GPIO, GPIO.OUT, initial=True)

        logging.info(f"Running for {seconds} seconds")
        GPIO.output(PUMP_GPIO, False)  # Turn on

        sleep(seconds)

        self.turn_off_pump()

        sleep(1)
        self.lastWatered = time.strftime('%Y-%m-%d %H:%M:%S')
        pubsub_service = PubSubService()
        pubsub_service.publish(TOPIC_DEVICE_LAST_WATERED, json.dumps(
            {"timestamp": self.lastWatered}))

    def turn_off_pump(self):
        if self.is_watering:
            logging.info("Turning off pump")
            GPIO.output(PUMP_GPIO, True)
            self.is_watering = False

            pubsub_service = PubSubService()
            pubsub_service.publish(TOPIC_WATERING_STOPED, json.dumps(
                {"status": "off"}))
        else:
            logging.warn("Pump is not running, no need to turn off")

    # Callback when the subscribed topic receives a message
    def on_start_event(self, topic, payload, dup, qos, retain, **kwargs):
        logging.info(
            "Received message from topic '{}': {}".format(topic, payload))
        try:
            message = json.loads(payload)
            self.run_pump(message['seconds'])
        except json.JSONDecodeError as e:
            logging.error("Failed to decode JSON payload: {}".format(e))

    def on_stop_event(self, topic, payload, dup, qos, retain, **kwargs):
        logging.info(
            "Received message from topic '{}': {}".format(topic, payload))
        try:
            self.turn_off_pump()
        except json.JSONDecodeError as e:
            logging.error("Failed to decode JSON payload: {}".format(e))

    def on_get_last_watered_event(self, topic, payload, dup, qos, retain, **kwargs):
        logging.info(
            "Received message from topic '{}': {}".format(topic, payload))
        try:
            pubsub_service = PubSubService()
            pubsub_service.publish(TOPIC_DEVICE_LAST_WATERED, json.dumps(
                {"timestamp": self.lastWatered}))
        except json.JSONDecodeError as e:
            logging.error("Failed to decode JSON payload: {}".format(e))

    def run(self):
        pubsub_service = PubSubService()
        pubsub_service.subscribe(TOPIC_WATERING_SMALL,
                                 lambda *args, **kwargs: threading.Thread(target=self.on_start_event, args=args, kwargs=kwargs).start())

        pubsub_service.subscribe(TOPIC_WATERING_STOP,
                                 lambda *args, **kwargs: threading.Thread(target=self.on_stop_event, args=args, kwargs=kwargs).start())

        pubsub_service.subscribe(TOPIC_DEVICE_LAST_WATERED_GET,
                                 lambda *args, **kwargs: threading.Thread(target=self.on_get_last_watered_event, args=args, kwargs=kwargs).start())

        logging.info("[plugin-small] waiting for a command!")
        received_all_event.wait()
        logging.info("[plugin-small] stopping the service!")
