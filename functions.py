import subprocess
from time import time
import ipaddress
import orjson
from loguru import logger


def fprint(message):
    print(message, flush=True)


def is_valid_ip(ipaddr):
    try:
        ipaddress.ip_address(ipaddr)
        return True
    except ValueError:
        return False


def get_tailscale_data() -> dict:
    try:
        output = subprocess.check_output(
            ["tailscale", "status", "--json"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        return orjson.loads(output.strip().encode("utf8"))
    except subprocess.CalledProcessError as exc:
        logger.error(exc)
        return {}


def get_tailscale_ip4() -> str:
    try:
        output = subprocess.check_output(
            ["tailscale", "ip", "-4"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        ip = output.strip()
        if is_valid_ip(ip):
            return ip
    except subprocess.CalledProcessError as e:
        logger.error(e)
    return ""


def get_tailscale_ip6() -> str:
    try:
        output = subprocess.check_output(
            ["tailscale", "ip", "-6"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        ip = output.strip()
        if is_valid_ip(ip):
            return ip
    except subprocess.CalledProcessError as e:
        logger.error(e)
    return ""


def a_record(ip):
    return "A" if ":" not in ip else "AAAA"
