from abc import abstractmethod, ABC
from typing import Optional, Union, List, Never, cast

from dns import rcode

from .pipeserver import PipeAbiVersion1


class QueryResponse:

    def __init__(
            self,
            qname: str,
            answer: Optional[Union[List[str], str]] = None,
            code: Optional[rcode] = None,
            qtype: Optional[str] = 'A',
            ttl: Optional[int] = 3600,
            _id: Optional[int] = 1,
    ) -> Never:
        """
        Instantiates a new ResponseModel object
        Determines the appropriate rcode based on the presence or absence of 'answer' and 'code'.

        Parameters:
        qname (str): The domain from the original query
        answer (Optional[Union[List[str], str]]): The DNS answer.
        code (Optional[rcode]): The response code.

        Returns:
        Never
        """
        self.qname = qname
        self.qtype = qtype
        self.ttl = ttl
        self.id = _id
        # Ensure answer is a list
        self.answer = [] if not answer else list(answer if isinstance(answer, list) else [answer])
        # determines code
        code = code if isinstance(code, rcode) else rcode.NOERROR if answer else rcode.SERVFAIL
        # Explicitly cast code to rcode to satisfy type checkers
        self.rcode = cast(rcode, code)

    def to_pipe(self):
        """
        Converts ResponseModel into a text representation suitable for PowerDNS
        DATA    example.org     IN  SOA 86400   1 ahu.example.org ...
        DATA    example.org     IN  NS  86400   1 ns1.example.org
        DATA    example.org     IN  NS  86400   1 ns2.example.org
        DATA    ns1.example.org IN  A   86400   1 203.0.113.210
        DATA    ns2.example.org IN  A   86400   1 63.123.33.135
        """
        return '\n'.join([
            '\t'.join(['DATA', self.qname, "IN", self.qtype, self.id, answer])
            for answer in self.answer
        ]) + "END\n"

    def to_json(self):

        records = []
        for answer in self.answer:
            records.append(
                {
                    "name": answer.name + '.',
                    "type": answer.type,
                    "TTL": answer.ttl,
                    "data": answer.content,
                },
            )

        return {
            "Status": self.rcode,
            "TC": "false",
            "RD": "false",
            "RA": "false",
            "AD": "false",
            "CD": "false",
            "Question": [
                {
                    "name": self.qname,
                    "type": self.qtype,
                }
            ],
            "Answer": [
                {
                    "name": self.qname + '.',
                    "type": self.qtype,
                    "TTL": self.ttl,
                    "data": answer,
                },
                {
                    "name": "example.com.",
                    "type": 1,
                    "TTL": 86400,
                    "data": "93.184.216.35"
                }
            ]
        }

    def to_wire(self):
        """
        Converts ResponseModel into wire format suitable for DNS53
        """
        pass




class DefaultState(PipeAbiVersion1):
    pass


class AbstractStateFactory(ABC):

    def __init__(self, dns_router):
        self.dns_router = dns_router
        self.state = None
        self.state_map = {}

    @abstractmethod
    def create_state(self, *args, **kwargs):
        pass

    @abstractmethod
    def change_state(self, obj, new_state):
        obj.state = new_state


class BaseResolverState(ABC):

    def __init__(self, resolver_state):
        self.dns_router = resolver_state

    @abstractmethod
    def resolve(self, *args, **kwargs) -> QueryResponse:
        # return self.dns_router.handle_request()
        pass


class BaseServer:

    @property
    @abstractmethod
    def name(self):
        return "Not_a_real_server"

    @abstractmethod
    def start(self, *args, **kwargs):
        pass


