import multiprocessing
from typing import List
from abstract import AbstractServer


class MultiServer:
    """
    Class to manage multiple server instances, each running in a separate process.
    """
    def __init__(self, servers: List[AbstractServer], **kwargs):
        """
        Initialize the MultiServer with a list of servers and a single DnsRouter instance.
        """
        self.kwargs = {}
        self.servers = servers
        self.dns_router = kwargs.get("dns_router")
        self.processes = []

    def start(self, **kwargs):
        """
        Start each server in a separate process.
        """
        self.kwargs = kwargs
        for server in self.servers:
            process = multiprocessing.Process(target=self._start_server_process, args=(server,))
            process.start()
            self.processes.append(process)

    def _start_server_process(self, server):
        """
        Start an individual server process.
        """
        server_instance = server(self.dns_router, **self.kwargs)  # Assuming each server takes a DnsRouter instance
        server_instance.start()

    def join_servers(self):
        """
        Wait for all server processes to complete.
        """
        for process in self.processes:
            process.join()



