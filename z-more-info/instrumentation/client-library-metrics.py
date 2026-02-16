## Examples of Client Library Metrics Types

# Counter - Only increases (requests, errors, tasks completed)

from prometheus_client import Counter
requests_total = Counter('http_requests_total', 'Total HTTP requests')
requests_total.inc()  # Increment by 1

# Gauge - Can go up or down (temperature, memory usage, queue size)

from prometheus_client import Gauge
temperature = Gauge('room_temperature_celsius', 'Room temperature')
temperature.set(23.5)

# Histogram - Observations in buckets (request duration, response sizes)

from prometheus_client import Histogram
request_duration = Histogram('http_request_duration_seconds', 'Request duration')
request_duration.observe(0.25)  # 250ms request

# Summary - Similar to histogram, calculates quantiles

from prometheus_client import Summary
request_latency = Summary('request_latency_seconds', 'Request latency')
request_latency.observe(0.15)


## Basic Usage Pattern

# 1. Import the library
pythonfrom prometheus_client import Counter, start_http_server

# 2. Define metrics
pythonrequests_total = Counter('myapp_requests_total', 'Total requests')

# 3. Instrument your code
pythondef handle_request():
    requests_total.inc()
    # Your application logic here

# 4. Expose metrics endpoint
pythonstart_http_server(8000)  # Metrics available at :8000/metrics

# 5. Configure Prometheus to scrape
yamlscrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['localhost:8000']