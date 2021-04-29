import argparse
import json

from Traceroute import Traceroute
from TraceConfig import TraceConfig

parser = argparse.ArgumentParser()
parser.add_argument("dest_addr")
parser.add_argument("-p", "--start-port", type=int, help="start udp port", default=33434)
parser.add_argument("-q", "--max-probs", type=int, help="max probs per ttl", default=3)
parser.add_argument("-w", "--timeout", type=float, help="timeout in seconds", default=5.0)
parser.add_argument("-m", "--max-ttl", type=int, help="max ttl", default=30)
parser.add_argument("-s", "--source-ip", type=str, help="source ip", default="")
parser.add_argument("-j", "--json", help="json format", action="store_true")
args = parser.parse_args()


def createConfig(from_args):
    start_port = int(from_args.start_port)
    if start_port < 0 or start_port > 65535:
        raise RuntimeError("Enter a correct port")
    max_probs = int(from_args.max_probs)
    if max_probs < 0:
        raise RuntimeError("Enter a correct max probs")
    timeout = int(from_args.timeout)
    if timeout < 0:
        raise RuntimeError("Enter a correct timeout")
    max_ttl = int(from_args.max_ttl)
    if max_ttl < 0:
        raise RuntimeError("Enter a correct max ttl")
    return TraceConfig(
        start_port=start_port,
        max_probs=max_probs,
        response_timeout_sec=timeout,
        max_ttl=max_ttl,
        source_address=args.source_ip,
        json=args.json
    )


config = createConfig(args)

new_traceroute = Traceroute(config, args.dest_addr)
results = new_traceroute.run()
if config.json:
    print(json.dumps([[r.__dict__ for r in rr] for rr in results]))
