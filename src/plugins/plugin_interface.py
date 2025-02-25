from abc import ABC, abstractmethod


class PluginInterface(ABC):

    @abstractmethod
    def run(self):
        pass
