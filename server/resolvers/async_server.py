import asyncio
import aiodns
import aiomcache
from typing import Dict, Tuple


class AsyncDNSServer:
    def __init__(self, host: str, port: int, db_path: str, cache_ttl: int):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.cache_ttl = cache_ttl
        self.cache = aiomcache.Client("127.0.0.1", 11211)  # Memcached server address

    async def query_db(self, name: str) -> Tuple[str, int]:
        """Asynchronously query tailscale."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT ip, ttl FROM records WHERE name = ?", (name,)
            ) as cursor:
                row = await cursor.fetchone()
                return row if row else (None, None)

    async def resolve(self, name: str, qtype: str) -> str:
        """Resolve the DNS query using cache or database."""
        cache_key = f"{name}_{qtype}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached.decode()

        ip, ttl = await self.query_db(name)
        if ip:
            await self.cache.set(cache_key, ip, exptime=ttl)
            return ip
        return "No record found"

    async def handle_query(self, request: aiodns.DNSQuery):
        """Handle incoming DNS queries."""
        print(f"Received query: {request.name} {request.qtype}")
        response = await self.resolve(request.name, request.qtype)
        return aiodns.DNSRecord(a=aiodns.DNSResult(response))

    async def run_server(self):
        """Run the DNS server."""
        resolver = aiodns.DNSServer(self.handle_query)
        await resolver.start(self.host, self.port)

        print(f"DNS Server running on {self.host}:{self.port}")
        while True:
            await asyncio.sleep(3600)  # Keep the server running


if __name__ == "__main__":
    server = AsyncDNSServer(
        host="0.0.0.0", port=53, db_path="dns_records.db", cache_ttl=300
    )
    asyncio.run(server.run_server())
