from abc import ABC, abstractmethod


class PluginInterface(ABC):
    @abstractmethod
    def water(self):
        pass
