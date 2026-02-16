# Structuring and Naming Metrics

## Metric Naming Best Practices

Follow Prometheus naming conventions for consistency and clarity.

### Basic Format

```
<namespace>_<name>_<unit>_<suffix>
```

**Examples:**
```
http_requests_total          # Counter
process_memory_bytes         # Gauge
http_request_duration_seconds # Histogram
api_response_size_bytes      # Summary
```

### Key Rules

**1. Use snake_case** (underscores, not camelCase or hyphens)
```
✅ http_requests_total
❌ httpRequestsTotal
❌ http-requests-total
```

**2. Include the unit** (seconds, bytes, ratio)
```
✅ http_request_duration_seconds
✅ process_memory_bytes
❌ http_request_duration  # What unit?
```

**3. Add metric type suffix**
```
_total      # Counters (always increasing)
_count      # Part of histogram/summary
_sum        # Part of histogram/summary
_bucket     # Histogram buckets
```

**4. Use base units** (seconds not milliseconds, bytes not kilobytes)
```
✅ request_duration_seconds (e.g., 0.150 = 150ms)
❌ request_duration_milliseconds
```

---

## Naming by Metric Type

### Counter - Use `_total` Suffix

Counters only increase. Name should reflect accumulated count.

```python
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests'
)
```

**Good counter names:**
- `http_requests_total`
- `tasks_completed_total`
- `errors_total`
- `bytes_transmitted_total`

**Bad:**
- `http_requests` (missing `_total`)
- `current_requests` (this is a gauge, not counter)

---

### Gauge - Current State

Gauges can increase or decrease. Name should reflect current value.

```python
active_connections = Gauge(
    'active_connections',
    'Current number of active connections'
)

memory_usage_bytes = Gauge(
    'memory_usage_bytes',
    'Current memory usage in bytes'
)
```

**Good gauge names:**
- `active_connections`
- `queue_size`
- `temperature_celsius`
- `memory_usage_bytes`

**Bad:**
- `connections_total` (sounds like a counter)
- `memory` (missing unit)

---

### Histogram - Use `_seconds` or `_bytes`

Histograms track distributions. Always include unit.

```python
request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds'
)

response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes'
)
```

**Good histogram names:**
- `http_request_duration_seconds`
- `db_query_duration_seconds`
- `http_response_size_bytes`

**Automatically creates:**
- `http_request_duration_seconds_bucket`
- `http_request_duration_seconds_sum`
- `http_request_duration_seconds_count`

---

### Summary - Similar to Histogram

```python
api_latency_seconds = Summary(
    'api_request_latency_seconds',
    'API request latency'
)
```

**Creates:**
- `api_request_latency_seconds_sum`
- `api_request_latency_seconds_count`

---

## Using Labels Effectively

Labels add dimensions to metrics. Use them wisely.

### Good Label Usage

```python
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Increment with labels
http_requests_total.labels(method='GET', endpoint='/api', status='200').inc()
```

**Query in PromQL:**
```promql
http_requests_total{method="GET", status="200"}
```

### Label Best Practices

**DO:**
- Use labels for dimensions (method, status, endpoint)
- Keep cardinality low (< 100 unique values per label)
- Use consistent label names across metrics

```python
✅ labels=['method', 'status', 'endpoint']
```

**DON'T:**
- Use labels for high-cardinality data (user IDs, timestamps, random UUIDs)
- Use labels for values that change constantly

```python
❌ labels=['user_id', 'request_id', 'timestamp']  # TOO MANY unique values
```

**Why avoid high cardinality?**
- Each unique label combination creates a new time series
- Too many time series = memory exhaustion and slow queries
- `user_id` label with 1M users = 1M time series!

---

## Complete Example

```python
from prometheus_client import Counter, Gauge, Histogram

# Counter - requests
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Gauge - current connections
active_connections = Gauge(
    'http_active_connections',
    'Current number of active HTTP connections'
)

# Histogram - request duration
request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Usage
http_requests_total.labels(method='GET', endpoint='/api', status='200').inc()
active_connections.set(42)
request_duration_seconds.labels(method='GET', endpoint='/api').observe(0.25)
```

---

## Common Patterns

### Application-Level Metrics

```
myapp_requests_total
myapp_errors_total
myapp_request_duration_seconds
```

### System-Level Metrics

```
process_cpu_seconds_total
process_memory_bytes
process_open_fds
```

### Business Metrics

```
orders_completed_total
revenue_dollars_total
users_active
```

---

## Quick Reference

| Metric Type | Suffix | Example |
|-------------|--------|---------|
| Counter | `_total` | `requests_total` |
| Gauge | none | `memory_bytes` |
| Histogram | `_seconds`, `_bytes` | `duration_seconds` |
| Summary | `_seconds`, `_bytes` | `latency_seconds` |

**Key takeaways:**
- Follow naming conventions strictly
- Include units in metric names
- Use labels for dimensions, not high-cardinality data
- Choose the right metric type for what you're measuring
- Consistency matters for querying and dashboards

---

## Extra Credit

Here's an alert for when a Linux system is at 80% or more of the file descriptors (files, sockets, pipes, std in/out/error) allowed. (Which is usually 1024.)

```yaml
- alert: HighFileDescriptorUsage
  expr: process_open_fds > 800
  for: 5m
  annotations:
    summary: "Process has {{ $value }} file descriptors open"
```

> Note: This particular alert will show no results unless the system goes above 800 file descriptors (fds). Your prometheus server will probably sit around 40 fds or so. Try the number 20 to get a result. 
