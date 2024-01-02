from typing import Union, List
from server import MyAuthoritah,
from settings import DEFAULT_TTL

class QueryResponse:
    def __init__(self, *args, **kwargs):
        pass


dns_router = MyAuthoritah()


@dns_router.tld("*.co", authority=True)
def handle_co(query):
    """
    Act as a TLD server and answer queries for the '.co' TLD based on the specified wildcard.
    :param query: DNS query to be processed.
    """

@handle_co.sld("mysite")
def mysite_co(query):
    """
    Act as a second-level domain (SLD) server for 'mysite.co' and handle DNS queries specific to this domain.
    :param query: DNS query to be processed.
    """

@dns_router.sld("*.example.com", authority=True)
def example_com(query):
    """
    Act as an SLD server and answer queries for subdomains of 'example.com' based on the specified wildcard.
    :param query: DNS query to be processed.
    """

@example_com.route('A')
def handle_a_record(query):
    """
    Handle DNS 'A' record queries for subdomains of 'example.com'.

    :param query: DNS query to be processed.
    :return: QueryResponse object containing the response for the 'A' record query.
    """
    return QueryResponse(query, "127.0.0.1")


@dns_router.domain("*.blah.net", authority=True)
def blah_net(query):
    pass


@blah_net.route('A')
def handle_a_record(query):
    # Logic to handle A record query
    if not query.subname:
        return Response(query, ["127.0.0.1", "0.0.0.0"])
    elif query.subname == "www":
        return Response(query, ["100.100.200.10", "100.100.205.5"])
    else:
        return Response(query)


@domain_com.route('MX')
def handle_mx_record(query):
    # Logic to handle MX record query
    return "MX record response"


@domain_com.route('SRV')
def handle_mx_record(query):
    # Logic to handle MX record query
    return "MX record response"
