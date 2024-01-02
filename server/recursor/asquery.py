import asyncio
import aiohttp
from async_doh.client import DoHClient


async def main():
    async with DoHClient() as client:
        result = await client.query("https://1.1.1.1/dns-query", "www.google.com", "A")
        print("query:", result)
        result = await client.query_json(
            "https://1.1.1.1/dns-query", "www.google.com", "A"
        )
        print("query_json:", result)


asyncio.run(main())
