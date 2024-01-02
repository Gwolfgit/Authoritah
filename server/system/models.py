from typing import Optional, Union, List, cast, Never
from enum import Enum
from abc import ABC
from dns import rcode, resolver
from .common import ensure_set
from settings import DEFAULT_TTL, DEBUG_MODE


class Response:

    def __init__(self, query: str, content: Union[str, List], **kwargs):
        self.qtype = kwargs.get("qtype", query.type)
        self.qclass = kwargs.get("qclass", "IN")
        self.qname = kwargs.get("qname", query.name)
        self.ttl = kwargs.get("ttl", DEFAULT_TTL)
        self.id = kwargs.get("id", 1)
        self.content = ensure_set(content)


class Query(Enum):
    ANY = "ANY"
    SOA = "SOA"


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


