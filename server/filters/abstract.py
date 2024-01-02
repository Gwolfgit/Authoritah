from abc import ABC, abstractmethod


class AbstractFilter(ABC):
    def __init__(self, capacity: int):
        pass

    @abstractmethod
    def fill(self, values: list[str]):
        pass

    @abstractmethod
    def is_valid_tld(self, tld):
        pass
