"""Asynchronous reputation API client"""
import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Set
from asyncio_throttle import Throttler
from reputation.cache import ReputationCache


class ReputationClient:
    def __init__(self, config, metrics):
        self.config = config
        self.metrics = metrics
        self.cache = ReputationCache(ttl=config.data['performance']['cache_ttl'])
        self.base_url = config.data['api']['base_url']
        self.auth_token = config.data['api']['auth_token']
        self.timeout = config.data['api']['timeout']
        self.max_retries = config.data['api']['max_retries']
        self.retry_delay = config.data['api']['retry_delay']

        # Rate limiting
        self.rps = config.data['performance']['requests_per_second']
        self.throttler = Throttler(rate_limit=self.rps)
        self.max_concurrent = config.data['performance']['max_concurrent_requests']

    async def check_domains(self, domains: Set[str]) -> List[Dict[str, Any]]:
        """Check reputation for multiple domains"""
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for domain in domains:
                task = self._check_single_domain(session, domain, semaphore)
                tasks.append(task)

            # Process domains with progress tracking
            from tqdm.asyncio import tqdm
            results = await tqdm.gather(*tasks, desc="Processing domains")

        return [r for r in results if r is not None]

    async def _check_single_domain(self, session: aiohttp.ClientSession,
                                   domain: str, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """Check reputation for a single domain"""
        async with semaphore:
            async with self.throttler:
                # Check cache first
                cached = await self.cache.get(domain)
                # if the domain is cached
                if cached:
                    # add the response time for the queried domain to the metrics requests response times array
                    self.metrics.add_request(cached['response_time'])
                    return cached
                # start timer for measuring query for uncached domain
                start_time = time.time()
                # manage max attempts for querying a domain
                for attempt in range(self.max_retries):
                    try:
                        # construct the ranking request for the domain
                        url = f"{self.base_url}/domain/ranking/{domain}"
                        headers = {'Authorization': f'Token {self.auth_token}'}

                        timeout = aiohttp.ClientTimeout(total=self.timeout)
                        async with session.get(url, headers=headers, timeout=timeout) as response:
                            if response.status == 200:
                                data = await response.json()
                                # calculate response time for queried domain
                                response_time = (time.time() - start_time) * 1000  # ms

                                result = {
                                    'domain': domain,
                                    'reputation': data.get('reputation', 0),
                                    'classification': self._classify_score(data.get('reputation', 0)),
                                    'categories': data.get('categories', []),
                                    'response_time': response_time,
                                    'query_source': 'PCAP'
                                }

                                # Cache result
                                await self.cache.set(domain, result)

                                # Update metrics for successful query
                                self.metrics.add_request(response_time, success=True)

                                return result

                            elif response.status == 429:  # Rate limited
                                await asyncio.sleep(self.retry_delay * (attempt + 1))
                            else:
                                self.metrics.add_request(0, success=False)

                    except asyncio.TimeoutError:
                        # Update metrics for unsuccessful query -  with timeout response time
                        self.metrics.add_request(self.timeout * 1000, success=False)

                    except Exception as e:
                        # Update metrics for unsuccessful query - with 0 response time - since we have encountered with an exception
                        self.metrics.add_request(0, success=False)
                    # manage max attempts mechanism
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))

                return None

    def _classify_score(self, score: int) -> str:
        """Classify reputation score"""
        if score <= 60:
            return "Untrusted"
        else:
            return "Trusted"