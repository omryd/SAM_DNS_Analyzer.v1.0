# DNS Reputation Analysis Tool

A high-performance DNS traffic analysis system that replays PCAP files, extracts DNS queries, and performs reputation lookups with comprehensive monitoring and reporting.

## Features

-  **High-Performance**: Asynchronous processing with configurable concurrency
-  **Real-time Monitoring**: Live statistics including QPS, response times, and success rates
-  **Caching**: TTL-based caching to reduce API calls
-  **Robust Error Handling**: Automatic retries with exponential backoff
-  **Comprehensive Reporting**: Export results in CSV or JSON format
-  **Rate Limiting**: Configurable RPS to control system load
-  **Graceful Shutdown**: Clean termination on timeout or interrupt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/omryd/SAM_DNS_Analyzer.v1.0
cd SAM_DNS_Analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
## Configuration

Edit `config.yaml` to customize:
- API settings (timeout, retries)
- Performance parameters (concurrency, RPS)
- Output format (output will be placed under src folder, where main.py is located)
- Cache TTL

## Usage

### Basic Usage
```bash
python src/main.py --pcap sample.pcap
```

### With Timeout
```bash
python src/main.py --pcap sample.pcap --timeout 60
```

### Custom Output Format
```bash
python src/main.py --pcap sample.pcap --output-format json
```

### Custom Configuration
```bash
python src/main.py --pcap sample.pcap --config custom_config.yaml
```

## Command Line Options

- `--pcap, -p`: Path to PCAP file (required)
- `--config, -c`: Path to configuration file (default: config.yaml)- `--timeout, -t`: Timeout in seconds (optional)
- `--output-format, -o`: Output format - csv or json (default: csv)

## Output

Results are saved with timestamp in the format:
- `dns_reputation_results_YYYYMMDD_HHMMSS.csv`
- `dns_reputation_results_YYYYMMDD_HHMMSS.json`

Each record contains:
- Domain name
- Reputation score (0-100)
- Classification (Trusted/Untrusted)
- Categories
- Query source
- Response time (ms)

## Monitoring

Real-time statistics displayed during execution:
- Queries per second (QPS)
- Total/Successful/Failed requests
- Average response time
- Max response time

## Performance Optimization

- **Concurrent Processing**: Configurable max concurrent requests
- **Rate Limiting**: Built-in throttling to respect API limits
- **Caching**: Reduces redundant API calls for repeated domains
- **Async I/O**: Non-blocking operations for maximum throughput
