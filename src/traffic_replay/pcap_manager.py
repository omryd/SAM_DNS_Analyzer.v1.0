"""PCAP file manager for DNS traffic extraction"""
from typing import Set
from scapy.all import rdpcap, DNS
import time


class PCAPManager:
    def __init__(self, metrics):
        self.metrics = metrics
        self.packets_sent = 0
        self.errors = 0
        self.start_time = None

    async def extract_domains(self, pcap_file: str) -> Set[str]:
        """Extract unique domains from PCAP file"""
        domains = set()
        self.start_time = time.time()

        try:
            # Read PCAP file
            packets = rdpcap(pcap_file)
            # for each recorded packet in PCAP file
            for packet in packets:
                try:
                    # Check if packet has DNS layer
                    if packet.haslayer(DNS):
                        # extract DNS information
                        dns = packet[DNS]

                        # Extract queries
                        if dns.qr == 0:  # DNS query
                            for i in range(dns.qdcount):
                                # if the DNS query has a question section, and a name to query
                                if dns.qd and dns.qd[i].qname:
                                    # extract queried domain name
                                    domain = dns.qd[i].qname.decode('utf-8').rstrip('.')
                                    # check validity of extracted domain name
                                    if self._is_valid_domain(domain):
                                        domains.add(domain)
                                        self.metrics.add_query()

                        # Extract responses
                        elif dns.qr == 1:  # DNS response
                            if dns.an: # the answer section is not empty
                                for i in range(dns.ancount):
                                    if hasattr(dns.an[i], 'rrname'):
                                        # extract rrname (domain name)
                                        domain = dns.an[i].rrname.decode('utf-8').rstrip('.')
                                        # check validity of extracted domain name
                                        if self._is_valid_domain(domain):
                                            domains.add(domain)
                                            self.metrics.add_query()

                        self.packets_sent += 1

                except Exception as e:
                    self.errors += 1
                    continue

            # Calculate QPS
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                qps = len(domains) / elapsed
                self.metrics.current_qps = qps

        except Exception as e:
            print(f"Error reading PCAP file: {e}")
            raise

        return domains

    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain name"""
        if not domain or domain == '.':
            return False

        # Filter out common invalid domains
        invalid_patterns = ['localhost', 'localdomain', '.local', '.invalid', 'in-addr.arpa']
        for pattern in invalid_patterns:
            if pattern in domain.lower():
                return False

        # Basic domain validation
        parts = domain.split('.')
        if len(parts) < 2:
            return False

        return True

    def get_stats(self):
        """Get current statistics"""
        return {
            'packets_sent': self.packets_sent,
            'errors': self.errors,
            'qps': self.metrics.current_qps
        }