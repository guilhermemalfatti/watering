import sys
from awscrt import mqtt
from awsiot import mqtt_connection_builder
import threading
from shared.const import AWS_IOT_ENDPOINT, CERTIFICATE_PATH, CLIENT_ID,  PRIVATE_KEY_PATH, PUMP_GPIO, ROOT_CA_PATH
import RPi.GPIO as GPIO
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PubSubService:
    _instance = None
    _initialized = False
    _init_lock = threading.Lock()
    _connection_ready = threading.Event()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PubSubService, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        with self._init_lock:
            if not hasattr(self, 'initialized'):
                self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
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

                logging.info(
                    f"Connecting to {AWS_IOT_ENDPOINT} with client ID '{CLIENT_ID}'...")
                connect_future = self.mqtt_connection.connect()

                # Future.result() waits until a result is available
                connect_future.result()

                self.initialized = True
                self._connection_ready.set()

                logging.info("Connected!")

    def disconnect(self):
        """Gracefully disconnect from MQTT broker"""
        try:
            if hasattr(self, 'mqtt_connection') and self.mqtt_connection:
                logging.info("\nDisconnecting from MQTT broker...")
                disconnect_future = self.mqtt_connection.disconnect()
                disconnect_future.result()  # Wait for disconnect to complete

                self._connection_ready.clear()
                PubSubService._initialized = False
                logging.info("Disconnected successfully")
        except Exception as e:
            logging.error(f"Error during disconnect: {e}")

    def publish(self, topic, payload):
        self._ensure_connected()
        try:
            response = self.mqtt_connection.publish(
                topic=topic,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                payload=payload
            )
            return response
        except Exception as e:
            logging.error(f"Error to publish: {e}")
            return None

    def subscribe(self, topic, callback):
        self._ensure_connected()
        try:
            logging.info("Subscribing to topic '{}'...".format(topic))
            subscribe_future, packet_id = self.mqtt_connection.subscribe(
                topic=topic,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=callback)

            subscribe_result = subscribe_future.result()
            logging.info("Subscribed with {}".format(
                str(subscribe_result['qos'])))
        except Exception as e:
            logging.error(f"Error to subscribe: {e} topic {topic}")

    def unsubscribe(self, topic):
        # Todo
        logging.info(f"Unsubscribed from {topic}")

    def _ensure_connected(self):
        """Wait for connection to be ready before proceeding"""
        self._connection_ready.wait()

    # Callback when connection is accidentally lost.
    def on_connection_interrupted(self, connection, error, **kwargs):
        logging.error("Connection interrupted. error: {}".format(error))

    # Callback when an interrupted connection is re-established.

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        logging.info("Connection resumed. return_code: {} session_present: {}".format(
            return_code, session_present))

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            logging.info(
                "Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(self.on_resubscribe_complete)

    def on_resubscribe_complete(self, resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        logging.info("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))

    # Callback when the connection successfully connects
    def on_connection_success(self, connection, callback_data):
        assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
        logging.info("Connection Successful with return code: {} session present: {}".format(
            callback_data.return_code, callback_data.session_present))

    # Callback when a connection attempt fails
    def on_connection_failure(self, connection, callback_data):
        assert isinstance(callback_data, mqtt.OnConnectionFailureData)
        logging.error("Connection failed with error code: {}".format(
            callback_data.error))

    # Callback when a connection has been disconnected or shutdown successfully
    def on_connection_closed(self, connection, callback_data):
        logging.info("Connection closed")
