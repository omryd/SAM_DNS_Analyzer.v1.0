"""Reporting and output management"""
import asyncio
import json
import csv
from datetime import datetime
from typing import List, Dict, Any
from colorama import Fore


class Reporter:
    def __init__(self, metrics, config):
        self.metrics = metrics
        self.config = config
        self.monitoring = True

    async def start_monitoring(self):
        """Start real-time monitoring"""
        update_interval = self.config.data['monitoring']['update_interval']

        while self.monitoring:
            stats = self.metrics.get_stats()

            # Clear line and print stats
            print(f"\r{Fore.GREEN}QPS: {stats['qps']:.1f} | "
                  f"{Fore.CYAN}Requests: {stats['total_requests']} | "
                  f"{Fore.YELLOW}Success: {stats['successful_requests']} | "
                  f"{Fore.RED}Failed: {stats['failed_requests']} | "
                  f"{Fore.MAGENTA}Avg RT: {stats['avg_response_time']:.0f}ms",
                  end='', flush=True)

            await asyncio.sleep(update_interval)

    async def save_results(self, results: List[Dict[str, Any]]):
        """Save results to file"""
        if not results:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.data['output']['results_file']}_{timestamp}"
        format_type = self.config.data['output']['format']

        if format_type == 'json':
            await self._save_json(results, f"{filename}.json")
        else:
            await self._save_csv(results, f"{filename}.csv")

        print(f"\n{Fore.GREEN}Results saved to {filename}.{format_type}")

    async def _save_json(self, results: List[Dict[str, Any]], filename: str):
        """Save results as JSON"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)

    async def _save_csv(self, results: List[Dict[str, Any]], filename: str):
        """Save results as CSV"""
        if not results:
            return

        keys = ['domain', 'reputation', 'classification', 'categories',
                'query_source', 'response_time']

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()

            for result in results:
                # Convert categories list to string
                if 'categories' in result and isinstance(result['categories'], list):
                    result['categories'] = ', '.join(result['categories'])
                writer.writerow(result)