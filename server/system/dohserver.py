import sys
import logging
import logging.handlers
from typing import Optional, List

import ssl
import uvicorn
import dns.resolver
import dns.rdatatype
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .base import BaseServer, BaseResolverState, QueryResponse


class DNSQuery(BaseModel):
    """
    Pydantic model representing a DNS query.
    """
    hostname: str
    record_type: Optional[str] = Field(default="A", description="The DNS record type (e.g., A, AAAA, MX, TXT)")


#
# DOH Resolver State
#

class JSONResolverState(BaseResolverState):

    def resolve(self, qname, qtype) -> QueryResponse:
        return self.dns_router.handle_request(qname, qtype)


class WireResolverState(BaseResolverState):

    def resolve(self, qname, qtype) -> QueryResponse:
        return self.dns_router.handle_request(qname, qtype)


#
# DOH Server
#


class DohServer(BaseServer):

    def __init__(self, dns_router):
        """
        Initialize the FastAPI application.
        """
        super().__init__(dns_router)
        self.dns_router = DohResolverState(dns_router)
        self.app = FastAPI()
        self.setup_routes()

    def start(self, **kwargs):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(
            kwargs.get("cert", '/etc/ssl/ssl-cert-snakeoil.pem'),
            keyfile=kwargs.get('keyfile', '/etc/ssl/ssl-cert-snakeoil.key')
        )
        uvicorn.run(
            self,
            host=kwargs.get("host", "0.0.0.0"),
            port=kwargs.get("port", 8443),
            ssl=ssl_context
        )

    @property
    def name(self):
        return "DNS_OVER_HTTPS"

    def setup_routes(self):
        """
        Set up the routes for the FastAPI application.
        """
        @self.app.get("/dns-query")
        async def dns_query(query: DNSQuery) -> List[str]:
            try:
                result = self.dns_router.resolve(query.hostname, query.record_type)
                return result.to_json()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
