import asyncio
from async_dns.core import types
from async_dns.resolver import ProxyResolver
from async_doh.client import patch


async def main():
    revoke = await patch()
    resolver = ProxyResolver(proxies=["https://dns.alidns.com/dns-query"])
    res, _ = await resolver.query("x.com", types.A)
    print(res)
    await revoke()


asyncio.run(main())
