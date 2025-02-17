import os

from plugins import load_plugins


def main():
    plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    plugins = load_plugins(plugin_dir)

    import concurrent.futures

    def run_plugin(plugin):
        try:
            plugin.water()
        except Exception as e:
            print(f"Error running plugin {plugin}: {e}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(run_plugin, plugin)
                   for plugin in plugins.values()]
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    main()
