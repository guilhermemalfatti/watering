import os
import concurrent.futures
from plugins import load_plugins
from pubsub import PubSubService
from shared.const import AWS_IOT_ENDPOINT, CERTIFICATE_PATH, CLIENT_ID,  PRIVATE_KEY_PATH, PUMP_GPIO, ROOT_CA_PATH, TOPIC_WATERING_SMALL, WateringAction


def run_plugin(plugin):
    try:
        plugin.run()
    except Exception as e:
        print(f"Error running plugin {plugin}: {e}")


def main():
    plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    plugins = load_plugins(plugin_dir)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(run_plugin, plugin)
                   for plugin in plugins.values()]
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    main()
