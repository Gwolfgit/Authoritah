import re
from time import time
from typing import Tuple, Union, Optional, List, Callable, TypeVar, ParamSpec
from functools import wraps
from server import QueryResponse, Query
from loguru import logger
from dns import rcode, resolver
from system.models import InitState

# TYPE_CHECKING = True


class Authoritah:
    _state = InitState

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Authoritah, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.routes = {}
        self.domain_patterns = {}

    def domain(self, domain_pattern: str, authority: bool = True) -> Callable:
        """
        Add a domain pattern to the local store.

        Example:
            my = Authoritah()
            @my.domain('example.com')
            def my_domain():
                pass

        Args:
            domain_pattern (str): A string representing the domain or wildcard to answer queries for.
            authority (bool): if we should act as an authoritative server for this domain Default: True
                              this will automatically generate SOA replies if you do not supply a route.

        Returns:
            decorator
        """
        def decorator(func):
            regex_pattern = re.escape(domain_pattern).replace(r"\*", ".*")
            domain_group = DomainGroup(domain_pattern, authority, self)
            self.domain_patterns[regex_pattern] = domain_group
            setattr(self, func.__name__, domain_group)
            return func

        return decorator

    def router(self, *record_types) -> Callable:
        """
        The router function is a decorator factory that accepts variable arguments (*record_types), each representing a record type.
        The decorator function wraps the function func. The wrapper function is the new function that will replace func.
        It can include logic to handle different record types if necessary. The record types are stored in wrapper.record_types for easy access elsewhere

        Example:
            @my_domain.router('A')
            def handle_A_record():
                # Function implementation for A record
                pass

            @my_domain.router('A', 'AAAA', 'CNAME')
            def handle_multiple_records():
                # Function implementation for A, AAAA, and CNAME records
                pass

        Args:
            record_types (str, str, str): String(s) representing records to answer queries for.

        Returns:
            decorator
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Implement logic that handles different record types
                # ...

                return func(*args, **kwargs)

            # Storing the record types for possible use by other decorators or logic
            wrapper.record_types = record_types

            return wrapper

        return decorator

    def handle_request(self, domain: str, record_type: str) -> QueryResponse:

        """
        This function processes a request according to our routes.
        Routes are returned in order of descending specificity

        Args:
            domain:
            record_type:

        Returns:
            QueryResponse()
        """
        records = []
        for pattern, domain_group in self.domain_patterns.items():
            if re.match(pattern, domain):
                if record_type in domain_group.routes:
                    answer, code = None, rcode.SERVFAIL
                    try:
                        record = domain_group.routes[record_type]()
                        if isinstance(record, str):
                            records.append(record)
                        elif isinstance(record, list):
                            records.extend(record)
                        code = rcode.NOERROR
                    except Exception as exc:
                        logger.error(exc)
                    finally:
                        return QueryResponse(
                            qname=domain,
                            answer=[
                                record for record
                                in records if record is not None
                            ],
                            code=code,
                        )
                elif record_type == Query.ANY:
                    for route in domain_group.routes:
                        try:
                            records.append(route())
                        except Exception as exc:
                            logger.error(exc)

                    return QueryResponse(
                        answer=[
                                   record for record
                                   in records if record is not None
                                ],
                        code=rcode.NOERROR
                    )
                elif record_type == Query.SOA and domain_group.SOA:
                    return QueryResponse(
                        answer=[
                            domain_group.SOA
                        ],
                        code=rcode.NOERROR
                    )

        if record_type in self.routes:
            try:
                return self.routes[record_type]()
            except Exception as exc:
                logger.error(exc)

        return QueryResponse(
            answer=[
                record for record
                in records if record is not None
            ],
            code=rcode.FAILED
        )


class DomainGroup:
    def __init__(self, domain_name: Union[List[str], str], authority: bool = True):
        self.domain_name = domain_name
        self.routes = {}
        self.SOA = self.generate_soa_record(domain_name) if authority else None

    def generate_soa_record(self, domain: str) -> Tuple[str, str, int, int, int, int, int]:
        """
        Generate the values for a valid SOA record given a domain name.

        :param domain: The domain name for which the SOA record is being created.
        :return: A tuple containing the SOA record components.
        """
        primary_ns = f"ns1.{domain}."
        responsible_party = f"hostmaster.{domain}."
        serial_number = int(time())
        refresh_interval = 86400  # 24 hours
        retry_interval = 7200  # 2 hours
        expire_time = 3600000  # 1000 hours
        negative_caching_ttl = 86400  # 24 hours

        return (primary_ns, responsible_party, serial_number, refresh_interval,
                retry_interval, expire_time, negative_caching_ttl)

    def route(self, record_type):
        def decorator(func):
            self.routes[record_type] = func
            return func

        return decorator
