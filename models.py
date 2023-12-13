import orjson
from typing import Any, Dict, Tuple
from functions import get_tailscale_ip4, get_tailscale_ip6
from pathlib import Path


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def load_config():
    with open(Path(Path(__file__).parent.resolve(), "config.json"), "r") as fd:
        return dotdict(orjson.loads(fd.read()))


class DefaultDict(dict):
    """
    A dictionary subclass that maintains default keys and values.
    """

    def __init__(self, default_values: Dict[Any, Any], *args, **kwargs):
        """
        Initialize the dictionary with default values and any additional provided values.

        :param default_values: A dictionary of default key-value pairs.
        """
        super().__init__()
        self.default_values = default_values
        self.update(self.default_values)

    def __setitem__(self, key, value):
        """
        Set a dictionary item. If the key is a default key, reset to default value.
        """
        if key in self.default_values:
            super().__setitem__(key, self.default_values[key])
        else:
            super().__setitem__(key, value)

    def __delitem__(self, key):
        """
        Delete a dictionary item. If the key is a default key, reset to default value.
        """
        if key in self.default_values:
            super().__setitem__(key, self.default_values[key])
        else:
            super().__delitem__(key)

    def pop(self, key, *args, **kwargs):
        """
        Pop a dictionary item. If the key is a default key, reset to default value.
        """
        if key in self.default_values:
            return self.default_values[key]
        return super().pop(key, *args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Update the dictionary. Default keys are reset to default values.
        """
        updates = dict(*args, **kwargs)
        super().update(
            {
                k: self.default_values[k] if k in self.default_values else updates[k]
                for k in updates
            }
        )


class MyAuthoritah:
    def __init__(self, cfg: dotdict):
        self.cfg = cfg
        self.data = {}
        self._relay = self.cfg.default_relay
        self._ip6 = get_tailscale_ip6()
        self._ip = get_tailscale_ip4()
        self._relays = {self._relay: 0}
        self.subdomains = self.cfg.subdomains
        self.domain = self.cfg.domain

    def __setitem__(self, key: str, value: Any):
        self.data[key] = value

    def __getitem__(self, key: str):
        return {
            key: {
                "A": self.get_ts_ip(),
                "SOA": f"{self.get_ns_id()}.{self.domain} hostmaster.{self.domain} 2023010101 7200 3600 1209600 3600",
                "AAAA": self.get_ts_ip6(),
                "NS": self.get_ns_domain(),
            }
        }

    def clear_counts(self):
        self._relays = {relay: 0 for relay in self._relays}

    def set_my_relay(self, relay: str):
        self._relay = relay

    def add_relay(self, relay: str):
        if relay in self._relays:
            self._relays[relay] += 1
        else:
            self._relays[relay] = 0

    def as_dict(self):
        return {
            domain: {
                "A": self.get_ts_ip(),
                "SOA": f"{self.get_ns_id()}.{self.domain} hostmaster.{self.domain} 2023010101 7200 3600 1209600 3600",
                "AAAA": self.get_ts_ip6(),
                "NS": self.get_ns_domain(),
            }
            for domain in self.get_my_domains()
        }

    def get_my_domains(self):
        domains = [
            f"{subdomain}.{self.domain}"
            for subdomain in [*self.subdomains, self.get_ns_id()]
        ]
        domains.append(self.domain)
        return domains

    def get_ns_domain(self):
        return f"{self.get_ns_id()}.{self.domain}"

    def get_my_relays_count(self):
        return self._relays[self._relay] + 1

    def set_ts_ip6(self, ip: str):
        self._ip6 = ip

    def get_ts_ip6(self):
        return self._ip6

    def set_ts_ip(self, ip: str):
        self._ip = ip

    def get_ts_ip(self):
        return self._ip

    def get_ns_id(self):
        return f"ns-{self._relay}{self.get_my_relays_count():02d}"
