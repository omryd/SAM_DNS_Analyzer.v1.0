"""
Main entry point for DNS Reputation Analysis Tool
"""
import asyncio
import signal
import sys
import time
from pathlib import Path
import click
from colorama import init, Fore

from traffic_replay.pcap_manager import PCAPManager
from reputation.api_client import ReputationClient
from monitoring.metrics import MetricsCollector
from monitoring.reporter import Reporter
from utils.config import Config

init(autoreset=True)  # Initialize colorama



class DNSReputationAnalyzer:
    def __init__(self, config_path: str):
        self.config = Config(config_path)
        self.metrics = MetricsCollector()
        self.reporter = Reporter(self.metrics, self.config)
        self.pcap_manager = PCAPManager(self.metrics)
        self.reputation_client = ReputationClient(self.config, self.metrics)
        self.shutdown_reason = None
        self.start_time = None

    async def analyze(self, pcap_file: str, timeout: int = None):
        """Main analysis workflow"""
        self.start_time = time.time()

        print(f"{Fore.GREEN}Starting DNS Reputation Analysis...")
        print(f"{Fore.CYAN}PCAP File: {pcap_file}")
        print(f"{Fore.CYAN}Timeout: {timeout if timeout else 'No limit'} seconds")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop\n")

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)

        try:
            # Start monitoring
            monitor_task = asyncio.create_task(self.reporter.start_monitoring())

            # Set timeout if specified
            if timeout:
                asyncio.create_task(self._timeout_handler(timeout))

            # Extract domains from PCAP
            print(f"{Fore.BLUE}Extracting DNS queries from PCAP...")
            domains = await self.pcap_manager.extract_domains(pcap_file)

            if not domains:
                print(f"{Fore.RED}No DNS queries found in PCAP file")
                return

            print(f"{Fore.GREEN}Found {len(domains)} unique domains")

            # Process domains
            print(f"{Fore.BLUE}Starting reputation lookups...")
            results = await self.reputation_client.check_domains(domains)

            # Save results
            await self.reporter.save_results(results)

            # Cancel monitoring
            monitor_task.cancel()

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"{Fore.RED}Error: {e}")
            self.shutdown_reason = "error"
        finally:
            await self._shutdown()

    async def _timeout_handler(self, timeout: int):
        """Handle timeout"""
        await asyncio.sleep(timeout)
        self.shutdown_reason = "timeout"
        raise asyncio.CancelledError()

    def _handle_interrupt(self, signum, frame):
        """Handle keyboard interrupt"""
        self.shutdown_reason = "keyboard interrupt"
        asyncio.create_task(self._shutdown())
        sys.exit(0)

    async def _shutdown(self):
        """Graceful shutdown"""
        runtime = time.time() - self.start_time if self.start_time else 0

        print(f"\n{Fore.YELLOW}{'=' * 50}")
        print(f"{Fore.RED}Test is over! Reason: {self.shutdown_reason or 'completed'}")
        print(f"{Fore.CYAN}Total runtime: {runtime:.1f} seconds")
        print(f"Requests total: {self.metrics.total_requests}")
        print(f"Domains processed: {self.metrics.successful_requests}")
        print(f"Average response time: {self.metrics.get_avg_response_time():.0f} ms")
        print(f"Max response time: {self.metrics.get_max_response_time():.1f} sec")
        print(f"{Fore.YELLOW}{'=' * 50}")

@click.command()
@click.option('--pcap', '-p', required=True, help='Path to PCAP file')
@click.option('--config', '-c', default='config.yaml', help='Path to config file')
@click.option('--timeout', '-t', type=int, help='Timeout in seconds')
@click.option('--output-format', '-o', type=click.Choice(['csv', 'json']), default='csv')
def main(pcap, config, timeout, output_format):
    """DNS Reputation Analysis Tool"""
    if not Path(pcap).exists():
        print(f"{Fore.RED}Error: PCAP file not found: {pcap}")
        sys.exit(1)

    analyzer = DNSReputationAnalyzer(config)

    if output_format:
        analyzer.config.data['output']['format'] = output_format

    try:
        asyncio.run(analyzer.analyze(pcap, timeout))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()