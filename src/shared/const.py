from enum import Enum


# AWS IoT Endpoint (Find it in AWS IoT Console > Settings)
AWS_IOT_ENDPOINT = "a3ec0i3g0gczud-ats.iot.us-east-2.amazonaws.com"

# Certificate Paths
CERTIFICATE_PATH = "/home/water-project/watering/IOT-core-aws/rasp-water.cert.pem"
PRIVATE_KEY_PATH = "/home/water-project/watering/IOT-core-aws/rasp-water.private.key"
ROOT_CA_PATH = "/home/water-project/watering/IOT-core-aws/root-CA.crt"

# MQTT Topic
TOPIC_WATERING_SMALL = "plants/watering/small"
TOPIC_WATERING_BUG = "plants/watering/big"
TOPIC_WATERING_STOP = "plants/watering/stop"
TOPIC_DEVICE_LAST_WATERED = "plants/device/lastWatered"
TOPIC_DEVICE_PING = "plants/device/ping"
TOPIC_DEVICE_PONG = "plants/device/pong"

CLIENT_ID = "raspbery-pi"


class WateringAction(Enum):
    ON = "on"
    OFF = "off"


# PUMP_GPIO = 4
PUMP_GPIO = 7
