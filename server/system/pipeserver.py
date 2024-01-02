import sys
from .base import BaseServer, BaseResolverState, AbstractStateFactory
from .models import QueryResponse
from logging import getLogger

logger = getLogger()
#
# PowerDNS Pipe Backend
#


class PipeStateFactory(AbstractStateFactory):
    def __init__(self, dns_router):
        super().__init__(dns_router)
        self.state_map = {
                0: PipeInitState,
                1: PipeAbiVersion1,
                2: PipeAbiVersion2,
                3: PipeAbiVersion3,
                5: PipeAbiVersion5,
                9: PipeFailedState,
            }
        self.state = PipeInitState(dns_router, self)

    def create_state(self, some_var):
        state_class = self.state_map.get(some_var, PipeAbiVersion1)
        return state_class(self.dns_router)

    def change_state(self, obj, new_state):
        obj.state = new_state


class PipeInitState:
    def __init__(self, dns_router, factory: PipeStateFactory):
        super().__init__(dns_router)
        self.factory = factory
        self.state = None  # Current state of the object

    def resolve(self, query: list) -> str:
        if query[1] == "HELO" and int(query[2]) in self.factory.state_map:
            self.factory.change_state(self, self.factory.create_state(int(query[2])))
            return "OK\tPython backend firing up\n"

        self.factory.change_state(self, self.factory.create_state(int(query[2])))
        return "FAIL\n"


class PipeFailedState:
    def __init__(self, factory: PipeStateFactory):
        self.factory = factory

    def resolve(self, *args, **kwargs) -> str:
        try:
            raise Exception
        except Exception as exc:
            logger.error(exc)
            return "FAIL\n"
        finally:
            exit(1)


class PipeAbiVersion1(PipeStateFactory):
    """
    #### QUESTION FORMAT - VERSION 1 [Default]
    Q qname qclass qtype id remote-ip-address

    #### ANSWER FORMAT - VERSION 1
    DATA qname qclass qtype ttl id content
    """
    def resolve(self, query: list) -> str:
        _q, qname, qclass, qtype, _id, remote_ip_address = query

        return self.dns_router.handle_request(qname, qtype).to_pipe(1)


class PipeAbiVersion2(PipeStateFactory):
    """
    #### QUESTION FORMAT - VERSION 2
    Q qname qclass qtype id remote-ip-address local-ip-address

    #### ANSWER FORMAT - VERSION 2
    DATA qname qclass qtype ttl id content
    """
    def resolve(self, query: list) -> str:
        _q, qname, qclass, qtype, _id, remote_ip_address, local_ip_address = query

        return self.dns_router.handle_request(qname, qtype).to_pipe(2)


class PipeAbiVersion3(PipeStateFactory):
    """
    #### QUESTION FORMAT - VERSION 3
    Q qname qclass qtype id remote-ip-address local-ip-address edns-subnet-address

    #### ANSWER FORMAT - VERSION 3
    DATA scopebits auth qname qclass qtype ttl id content
    """
    def resolve(self, query: list) -> str:
        _q, qname, qclass, qtype, _id, remote_ip_address, local_ip_address, edns_subnet_address = query

        return self.dns_router.handle_request(qname, qtype).to_pipe(3)


class PipeAbiVersion5(PipeStateFactory):
    """
    #### QUESTION FORMAT - VERSION 5
    Q qname qclass qtype id remote-ip-address local-ip-address edns-subnet-address

    #### ANSWER FORMAT - VERSION 5
    DATA scopebits auth qname qclass qtype ttl id content
    """
    def resolve(self, query: list) -> QueryResponse:
        _q, qname, qclass, qtype, _id, remote_ip_address, local_ip_address, edns_subnet_address = query

        return self.dns_router.handle_request(qname, qtype).to_pipe(3)


class PipeServer(BaseServer):

    def __init__(self, dns_router, **kwargs):
        """Main function to run the service."""
        self.dns_router = PipeInitState(dns_router)

    def name(self):
        return "PowerDNS_Pipe_Backend"

    def start(self, *args, **kwargs):
        try:
            for line in sys.stdin:
                answer = self.dns_router.resolve(line.strip().split("\t"))
                # Write answer to stdout
                print(answer, flush=True)

        except KeyboardInterrupt:
            pass
        finally:
            exit(0)



