from abc import ABCMeta, abstractmethod


class Plot(metaclass=ABCMeta):

    @abstractmethod
    def plot(self):
        pass
