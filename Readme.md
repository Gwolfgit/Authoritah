# Authoritah

Authoritah is a dynamic DNS server designed for use within a Tailscale network. It facilitates latency-based 
load balancing and routing by responding to DNS queries with the Tailscale IP address of the Edge node it's 
running on. This ensures that requests are routed to the closest node relative to the user in the tailnet, 
optimizing response times and network efficiency.

## Features

- Dynamic DNS Responses: Replies to DNS queries with the Tailscale IP address of the local Edge node.
- Latency-Based Load Balancing: Ensures requests are handled by the closest node in the Tailscale network to reduce latency.
- Tailscale Integration: Seamlessly works with Tailscale’s MagicDNS feature, making it ideal for distributed networks.
- Simple Setup: Easy to configure and deploy on each Edge node in a Tailscale network.

## Usage

Authoritah is designed to work within a Tailscale network, specifically leveraging Tailscale's MagicDNS feature. When configured properly, Authoritah allows for efficient and latency-optimized domain name resolution within your Tailscale network.
How Tailscale Queries Authoritah

When you use Tailscale's MagicDNS feature, Tailscale can be configured to recognize custom domains. For example, if you configure yourdomain.com in MagicDNS and list the IPs of all your nodes running Authoritah as nameservers for this domain, Tailscale will query these nameservers for DNS resolution.

Here’s how it works:

**Query Distribution**: When a device in your Tailscale network attempts to access yourdomain.com, Tailscale sends DNS queries to every nameserver configured for yourdomain.com. This means it will send queries to each of your nodes running Authoritah.

**Response from Authoritah**: Each instance of Authoritah, running on different nodes, is programmed to respond to queries with its own Tailscale IP address. Therefore, every node will respond with a different IP address based on its location in the network.

**First Response Handling**: Tailscale uses the first response it receives. Given that the network latency between the querying device and each Authoritah node can vary, the first response typically comes from the geographically closest node. This mechanism inherently creates a latency-based load balancing system.

**Routing to the Closest Node**: As a result, the requesting device in the Tailscale network is directed to the closest node hosting the requested service or content, minimizing response times and improving overall network efficiency.

### Configuring Your Domain with Tailscale

To set up Authoritah with Tailscale, follow these steps:

- Configure yourdomain.com in Tailscale's MagicDNS settings.
    Add the Tailscale IP addresses of all your nodes running Authoritah as nameservers for yourdomain.com.
    Ensure Authoritah is running on each of these nodes.

## Requirements

    Tailscale network setup
    Python 3.6 or higher
    Required Python modules: orjson, redis_dict, loguru
    PowerDNS with Pipe backend
    Redis (optional)

### Installation
1) Clone the repository:
```commandline
git clone https://github.com/Gwolfgit/Authoritah.git
cd Authoritah
```
2) Create a venv and Install the necessary Python dependencies:
```commandline
python3 -m venv venv
. venv/bin/activate
pip install -r req.txt
```
3) Rename config.exmaple.json to config.json and configure to your specific settings.
```commandline
mv config.example.json config.json
vi config.json
```
4) Configure PowerDNS to use the backend.
```/etc/powerdns/pdns.conf or pdns.d/file.conf
launch=pipe
pipe-command=/etc/powerdns/Authoritah/main.py
pipe-regex=^\w*\.*example\.com$
```
5) Ensure that main.py is set executable and that the shebang matches your venv.
```commandline
cat main.py | grep '#!'
"#!/path/to/venv/python3"
# set /path/to/venv/python3 to the same value as:
which python3
chmod +x main.py
```
6) You can test it like this:
```commandline
# in tty 1
pdns_server
# in tty 2
dig @localhost www.example.com
```

## Notes
After publishing this, I realized that I had forgotten to mention that I used Redis as 
a cache to prevent repeated blocking calls to tailscale. I quickly wrote up a drop-in replacement 
for the redis dependency which allows you to cache in volatile memory instead of redis. Just in case.
The file optional.py contains a class and a monkey patch redis.StrictRedis = LooseRedis.
