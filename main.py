#!/etc/powerdns/venv/bin/python3
import json
import sys
from uuid import uuid4
from loguru import logger
from redis_dict import RedisDict
from models import *
from functions import *


Cfg = load_config()
UUID = uuid4().hex[:8]
RESULT_CACHE = RedisDict(namespace=f'Authoritah:{UUID}', expire=Cfg.local_cache_expire)
Authoritah = MyAuthoritah(Cfg)


def refresh_index():
    ts_data = get_tailscale_data()
    Authoritah.clear_counts()
    Authoritah.set_ts_ip(get_tailscale_ip4())
    Authoritah.set_ts_ip6(get_tailscale_ip6())
    Authoritah.set_my_relay(ts_data.get("Self", {}).get("Relay", "den"))
    RESULT_CACHE["ZONES"] = Authoritah.as_dict()
    RESULT_CACHE["LAST_REFRESH"] = time()

    for node, data in ts_data["Peer"].items():
        Authoritah.add_relay(data.get("Relay", "default"))

        RESULT_CACHE["ZONES"][data.get("DNSName")] = {
            a_record(ip): ip for ip in data.get("TailscaleIPs", [])
        }


class DNSZone:
    def __init__(self, zone: str):
        self.zone = zone
        self.expires = Cfg.dns_record_expires
        self.fileout = sys.stdout
        self.zone_data = RESULT_CACHE.get("ZONES").get(zone.lower(), [])
        self.prefix = ["DATA", str(zone), "IN"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        fprint("END")

    def any_query(self):
        for record_type, record in self.zone_data.items():
            fprint(
                "\t".join(
                    [
                        *self.prefix,
                        str(record_type),
                        str(self.expires),
                        "-1",
                        str(record),
                    ]
                )
            )

    def execute(self, query_type: str):
        if not self.zone_data:
            return fprint("LOG\tNo records found for {}".format(self.zone))
        if query_type.upper() == "ANY":
            return self.any_query()
        try:
            answer = self.zone_data[query_type]
            query_type = "A" if query_type == "Q" else query_type
            return fprint(
                "\t".join(
                    [*self.prefix, str(query_type), str(self.expires), "-1", str(answer)]
                )
            )
        except KeyError:
            return fprint("LOG\tNo {} records found for {}".format(str(query_type), self.zone))


class StateFactory:
    def __init__(self):
        self.state = InitState(self)

    def change_state(self, new_state):
        self.state = new_state(self)

    def handle_query(self, query: list):
        self.state.query(query)


class InitState:
    def __init__(self, factory: StateFactory):
        self.factory = factory

    def query(self, query: list):
        """
        Processes the given query.
        The only accepted query is "HELO 1", which changes the state to ConnectedState.
        Any other query results in a failure response.

        :param query: A list representing the query parameters.
        """
        if tuple(query[:2]) == ("HELO", "1"):
            self.factory.change_state(ConnectedState)
            return fprint("OK\tPython backend firing up")
        else:
            fprint("FAIL")


class ConnectedState:
    def __init__(self, factory: StateFactory):
        self.factory = factory

    def query(self, query: list):
        _type, qname, qclass, qtype, _id, ip = query
        with DNSZone(qname) as resolver:
            resolver.execute(qtype)


class FailedState:
    def __init__(self, factory: StateFactory):
        self.factory = factory

    def query(self, query: list):
        fprint("FAIL")


class PipeResolver:
    def __init__(self):
        self.state_factory = StateFactory()
        self.process_requests()

    def process_requests(self):
        while True:
            if "LAST_REFRESH" not in RESULT_CACHE:
                refresh_index()

            line = sys.stdin.readline().rstrip()
            if line == "":
                logger.debug("EOF")
                break

            query = line.split("\t")
            self.state_factory.handle_query(query)


if __name__ == "__main__":
    try:
        PipeResolver()
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        logger.debug(f"execution failure: {e}")
        raise
