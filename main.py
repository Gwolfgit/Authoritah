import sys
from server import PipeServer, DohServer, UDPServer, MultiServer
from routes import dns_router


# This is the default.
# If you run it directly,
# you'll see a message on stderr
# Usage: main.py --pipe or just main.py
def run_pipe_server():
    PipeServer(dns_router)


# Doh Server
# Usage: main.py --doh -c /path/to/cert.pem -k /path/to/key.pem [-h bind-address] [-p bind-port]
def run_doh_server(cert, key, host="127.0.0.1", port=8443):
    DohServer(dns_router).start(cert, keyfile=key, host=host, port=port)


# Run just the UDP Server
# main.py --udp [-listen address:port]
def run_udp_server(udp_host="127.0.0.1", udp_port=5353):
    UDPServer(dns_router).start(host=udp_host, port=udp_port)


# Optionally, you can run both the Doh Server and the UDP Server together
# Usage:
# --multi -cert /path/to/cert.pem -key /path/to/key.pem -bind address:tcp-port -listen address:udp-port
# This callable can also accept custom server classes
def run_multi_server(*args, **kwargs):
    multi_server = MultiServer(
        [DohServer, UDPServer],
        router=dns_router,
        cert=kwargs.get("cert"),
        keyfile=kwargs.get("key"),
        bind=kwargs.get("bind"),
        listen=kwargs.get("listen"),
    )
    multi_server.start()
    multi_server.join_servers()


if __name__ == "__main__":
    sys.stderr.write("This is the Pipe Backend server, did you start it by accident?")
    sys.stderr.write("Hit Control+C to exit and then try --help")
    sys.stderr.write("Otherwise, you can ignore this message.")
    run_pipe_server()


