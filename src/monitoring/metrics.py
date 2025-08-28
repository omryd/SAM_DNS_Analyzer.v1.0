"""Metrics collection for monitoring"""
import time
from typing import List, Dict, Any
import statistics


class MetricsCollector:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times: List[float] = []
        self.current_qps = 0
        self.queries_count = 0
        self.start_time = time.time()

    def add_request(self, response_time: float, success: bool = True):
        """Record a request"""
        self.total_requests += 1
        self.response_times.append(response_time)

        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

    def add_query(self):
        """Record a DNS query"""
        self.queries_count += 1
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            self.current_qps = self.queries_count / elapsed

    def get_avg_response_time(self) -> float:
        """Get average response time in ms"""
        if self.response_times:
            return statistics.mean(self.response_times)
        return 0

    def get_max_response_time(self) -> float:
        """Get max response time in seconds"""
        if self.response_times:
            return max(self.response_times) / 1000
        return 0

    def get_min_response_time(self) -> float:
        """Get min response time in ms"""
        if self.response_times:
            return min(self.response_times)
        return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        return {
            'qps': self.current_qps,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'avg_response_time': self.get_avg_response_time(),
            'max_response_time': self.get_max_response_time(),
            'min_response_time': self.get_min_response_time()
        }