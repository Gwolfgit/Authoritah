import asyncio
import subprocess
import logging
from datetime import datetime, timedelta
import orjson
import cachetools
from settings import CONFIG, DEFAULT


logger = logging.getLogger(__name__)


def get_tailscale_data() -> dict:
    """
    Gets Tailscale data from cache or triggers an asynchronous cache refresh if needed.
    Communication with the server (PowerDNS) needs to remain synchronous.
    This pattern prevents our subprocess call from blocking the main thread.

    :return: A dictionary representing the Tailscale data.
    """
    now = datetime.now()
    # This sets our refresh threshold to 75% of the max expiration time.
    # The performance cost of the small calculation to determine the 75%
    # mark is negligible compared to the benefit of having fresher data available.
    refresh_threshold = cache["expiry"] - timedelta(
        minutes=(Cfg.local_cache_expire * 0.25)
    )

    if cache["data"] is None or now >= refresh_threshold:
        # Trigger async cache refresh but don't wait for it
        asyncio.create_task(refresh_cache())
        # Return stale data for now, or handle no data scenario
        return cache["data"] if cache["data"] else {}

    return cache["data"]


async def refresh_cache():
    """
    Asynchronously refreshes the cache with updated Tailscale data.
    """
    try:
        process = await asyncio.create_subprocess_exec(
            "tailscale",
            "status",
            "--json",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logger.error(f"Subprocess error: {stderr.decode()}")
            return

        cache["data"] = orjson.loads(stdout)
        cache["expiry"] = datetime.now() + timedelta(
            minutes=Cfg.local_cache_expire
        )  # Example expiry time
    except (subprocess.SubprocessError, OSError) as exc:
        logger.error(f"Exception occurred: {exc}")
