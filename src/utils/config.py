"""Configuration management"""
import yaml
from pathlib import Path


class Config:
    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = Path(config_path)
        self.data = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            return self._default_config()

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        """Return default configuration"""
        return {
            'api': {
                'base_url': 'https://microcks.gin.dev.securingsam.io/rest/Reputation+API/1.0.0',
                'auth_token': 'I_am_under_stress_when_I_test',
                'timeout': 5,
                'max_retries': 3,
                'retry_delay': 1
            },
            'performance': {
                'max_concurrent_requests': 50,
                'requests_per_second': 100,
                'cache_ttl': 3600
            },
            'monitoring': {
                'update_interval': 1
            },
            'output': {
                'results_file': 'dns_reputation_results',
                'format': 'csv'
            }
        }