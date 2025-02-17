from plugins.plugin_interface import PluginInterface
import time


class SmallPlantsWatering(PluginInterface):
    def water(self):
        while True:
            print(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Watering small plants", flush=True)
            time.sleep(1)
