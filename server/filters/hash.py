from .abstract import AbstractFilter


class HashFilter(AbstractFilter):
    def __init__(self, capacity: int = 1500):
        self.hash = set()
        super().__init__(capacity)

    def fill(self, values: list[str]):
        self.hash = set(values)

    def is_valid_tld(self, tld):
        return tld in self.hash
