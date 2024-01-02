import sys
import logging
import logging.handlers
import threading
import queue
from typing import Any


class RequestHandler:
    """Processes individual requests."""

    def __init__(self, request_queue: queue.Queue):
        self.request_queue = request_queue

    def run(self):
        while True:
            request = self.request_queue.get()
            if request is None:
                # Sentinel to shut down
                break
            self.process_request(request)

    def process_request(self, request: Any):
        # Process the request here
        # For example, echo the request
        print(f"Processed: {request}", file=sys.stdout)


class PipeResolver:
    def __init__(self):
        self.state_factory = StateFactory()
        self.process_requests()

    def process_request(self):
        while True:
            if "LAST_REFRESH" not in RESULT_CACHE:
                refresh_index()

            line = sys.stdin.readline().rstrip()
            if line == "":
                logger.debug("EOF")
                break

            query = line.split("\t")
            self.state_factory.handle_query(query)
