
import socket
import time
import struct

import typing as tp

from TraceConfig import TraceConfig
from TraceResult import TraceResult


class Traceroute(object):
    def __init__(self, config: TraceConfig, destination: str):
        self.dest_name = destination
        self.config = config

    def create_sender_socket(self, ttl):
        send_socket = socket.socket(family=socket.AF_INET,
                                    type=socket.SOCK_DGRAM,
                                    proto=socket.IPPROTO_UDP)

        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        return send_socket

    def create_receiver_socket(self):
        recv_socket = socket.socket(family=socket.AF_INET,
                                    type=socket.SOCK_RAW,
                                    proto=socket.IPPROTO_ICMP)

        try:
            recv_socket.bind((self.config.source_address, 0))
        except socket.error as err:
            raise IOError('Unable to bind receiver socket: {}'.format(err))

        return recv_socket

    def run(self) -> tp.List[tp.List[TraceResult]]:
        results = []
        for ttl in range(1, self.config.max_ttl + 1):
            probes = []
            dest_port = self.config.start_port
            for probe_num in range(self.config.max_probs):
                probe_result = self.probe(ttl, dest_port)
                probes.append(probe_result)
                if not self.config.json:
                    if probe_result.resolved:
                        print("{}\t{} ({}) {:.2f} ms".format(
                            probe_result.ttl, probe_result.hostname, probe_result.addr[0], probe_result.time
                        ))
                    else:
                        print("{}\t*".format(probe_result.ttl))
                if probe_result.resolved:
                    break
                dest_port += 1

            results.append(probes)
            if any([prob.finished for prob in probes]):
                if not self.config.json:
                    print("Finished")
                return results
        return results

    def probe(self, ttl, dest_port) -> TraceResult:
        start_time = time.time()
        recv_socket = self.create_receiver_socket()
        send_socket = self.create_sender_socket(ttl)

        curr_addr = None
        curr_host_name = None
        total_time = 0.0
        try:
            send_socket.sendto(b'', (self.dest_name, dest_port))
            recv_socket.settimeout(self.config.response_timeout_sec)
            data, curr_addr = recv_socket.recvfrom(4048)

            icmpFormat = 'bbHHh'
            icmp_header = struct.unpack(icmpFormat, data[20:28])
            try:
                curr_host_name = str(socket.gethostbyaddr(curr_addr[0])[0])
            except Exception as e:
                pass
            finally:
                if curr_host_name is None:
                    curr_host_name = curr_addr[0]
        except Exception as e:
            return TraceResult(ttl=ttl)
        finally:
            recv_socket.close()
            send_socket.close()
            end_time = time.time()
            total_time = round((end_time - start_time) * 1000, 2)

        if curr_addr is not None:
            traceResult = TraceResult(ttl=ttl, resolved=True, hostname=curr_host_name, addr=curr_addr, time=total_time)
            if icmp_header[0] == 3 and icmp_header[1] == 3:
                traceResult.finished = True
                return traceResult
            if total_time > self.config.response_timeout_sec * 1000:
                return TraceResult(ttl=ttl)
            return traceResult
        return TraceResult(ttl=ttl)


