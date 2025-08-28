import pytest
from src.reputation.cache import ReputationCache
from src.monitoring.metrics import MetricsCollector


@pytest.mark.asyncio
async def test_cache():
    """Test caching functionality"""
    cache = ReputationCache(ttl=60)

    test_data = {
        'domain': 'example.com',
        'reputation': 85,
        'classification': 'Trusted'
    }

    await cache.set('example.com', test_data)
    result = await cache.get('example.com')

    assert result == test_data
    assert cache.size() == 1

def test_metrics():
    """Test metrics collection"""
    metrics = MetricsCollector()

    metrics.add_request(100, success=True)
    metrics.add_request(200, success=True)
    metrics.add_request(150, success=False)

    assert metrics.total_requests == 3
    assert metrics.successful_requests == 2
    assert metrics.failed_requests == 1
    assert metrics.get_avg_response_time() == 150


if __name__ == "__main__":
    pytest.main([__file__])