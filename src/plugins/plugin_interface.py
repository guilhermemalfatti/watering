from abc import ABC, abstractmethod
from awscrt import mqtt, http
import sys


class PluginInterface(ABC):

    @abstractmethod
    def run(self):
        pass
