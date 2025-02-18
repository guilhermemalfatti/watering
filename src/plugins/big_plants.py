from plugins.plugin_interface import PluginInterface
import time


class BigPlantsWatering(PluginInterface):
    def water(self):
        print(
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Watering big plants", flush=True)
        # while True:
        #     print(
        #         f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Watering big plants", flush=True)
        #     time.sleep(1)
