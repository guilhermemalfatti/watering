from enum import Enum


# AWS IoT Endpoint (Find it in AWS IoT Console > Settings)
AWS_IOT_ENDPOINT = "a3ec0i3g0gczud-ats.iot.us-east-2.amazonaws.com"

# Certificate Paths
CERTIFICATE_PATH = "/home/water-project/watering/IOT-core-aws/rasp-water.cert.pem"
PRIVATE_KEY_PATH = "/home/water-project/watering/IOT-core-aws/rasp-water.private.key"
ROOT_CA_PATH = "/home/water-project/watering/IOT-core-aws/root-CA.crt"

# MQTT Topic
MQTT_TOPIC = "plants/watering/big"

CLIENT_ID = "raspbery-pi"


class WateringAction(Enum):
    ON = "on"
    OFF = "off"
