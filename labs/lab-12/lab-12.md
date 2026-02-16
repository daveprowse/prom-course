# ⚙️ Lab 12 - Instrumentation with OpenTelemetry and Prometheus

In this lab we will:

- Install OpenTelemetry (OTEL) SDK for Python
- Instrument a simple application with OTEL
- Export metrics in Prometheus format
- Scrape OTEL metrics with Prometheus

## What is OpenTelemetry?

**OpenTelemetry (OTEL)** is a vendor-neutral observability framework for:
- Metrics
- Traces  
- Logs

**Key difference from Prometheus client libraries:**
- **Prometheus libraries:** Prometheus-only, metrics-focused
- **OTEL:** Works with multiple backends (Prometheus, Jaeger, Datadog, etc.)

**When to use OTEL:**
- Multi-backend observability strategy
- Need traces AND metrics from same instrumentation
- Cloud-native applications with vendor flexibility
- Standardization across microservices

> Note: OTEL is an SDK/library (installed via pip), not a standalone application. The optional OTEL Collector is a separate component for advanced use cases.

---

## Install OpenTelemetry

Install the OTEL SDK and Prometheus exporter:

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-prometheus
```

> Note: Use `--break-system-packages` on Debian if needed.

Verify installation:

```bash
python3 -c "import opentelemetry; print('OTEL installed successfully')"
```

---

## Copy the Application File

The OTEL-instrumented application is provided in this lab directory as `otel_app.py`.

Copy it to your working directory and make it executable:

```bash
chmod +x otel_app.py
```

### Understanding the Application

The application simulates an HTTP server with OTEL instrumentation:

**Metrics created:**
- `http_requests_total` - Counter tracking total requests
- `http_active_requests` - UpDownCounter (gauge-like) for current active requests
- `http_request_duration_seconds` - Histogram for request latency

**Key OTEL concepts demonstrated:**
- Creating a `Meter` (namespace for metrics)
- Using `create_counter()`, `create_up_down_counter()`, and `create_histogram()`
- Adding attributes (labels) to metrics: `method`, `endpoint`, `status`
- Exporting to Prometheus format

---

## Run the Application

Start the application:

```bash
python3 otel_app.py
```

Output:
```
OTEL metrics server started on :8200
Metrics available at http://localhost:8200/metrics

GET /api/users -> 200
POST /api/products -> 201
GET / -> 200
```

> Note: Port 8200 is used to avoid conflicts with previous labs.

---

## Verify OTEL Metrics

In another terminal, check the metrics endpoint:

```bash
curl http://localhost:8200/metrics
```

You should see Prometheus-formatted metrics:

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/",method="GET",status="200"} 5.0

# HELP http_active_requests Current active HTTP requests  
# TYPE http_active_requests gauge
http_active_requests{endpoint="/api/users",method="GET"} 0.0

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{endpoint="/",method="GET",le="0.0"} 0.0
http_request_duration_seconds_bucket{endpoint="/",method="GET",le="5.0"} 3.0
...
```

**Notice:** OTEL automatically exports in Prometheus format!

---

## Configure Prometheus to Scrape OTEL Metrics

Edit `/etc/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'otel-app'
    static_configs:
      - targets: ['localhost:8200']
```

Reload Prometheus:

```bash
sudo systemctl reload prometheus
```

---

## Query OTEL Metrics in Prometheus

Access the Prometheus Web UI at `http://localhost:9090`

### Query 1: Total Requests

```promql
http_requests_total
```

View in Table mode. Notice the OTEL labels (method, endpoint, status).

### Query 2: Request Rate by Endpoint

```promql
sum by(endpoint) (rate(http_requests_total[1m]))
```

Shows requests per second grouped by endpoint.

### Query 3: Success Rate

```promql
sum(rate(http_requests_total{status=~"2.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
```

Percentage of 2xx responses.

### Query 4: Request Duration (p95)

```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

95th percentile latency across all requests.

### Query 5: Requests by Method

```promql
sum by(method) (rate(http_requests_total[1m]))
```

Compare GET vs POST vs PUT vs DELETE traffic.

---

## OTEL vs Prometheus Client Library

### Similarities

Both expose metrics on `/metrics` endpoint in Prometheus format.

### Key Differences

**Prometheus Client Library:**
```python
from prometheus_client import Counter

counter = Counter('requests_total', 'Total requests')
counter.inc()  # Increment
```

**OpenTelemetry:**
```python
from opentelemetry import metrics

meter = metrics.get_meter("app")
counter = meter.create_counter('requests_total', 'Total requests')
counter.add(1)  # Add value
```

**OTEL advantages:**
- ✅ Vendor-neutral (works with Jaeger, Datadog, Grafana Cloud, etc.)
- ✅ Unified SDK for metrics, traces, and logs
- ✅ Auto-instrumentation for popular frameworks
- ✅ Consistent API across languages

**Prometheus advantages:**
- ✅ Simpler and more lightweight
- ✅ Prometheus-native (no translation layer)
- ✅ Smaller dependency footprint

---

## Understanding OTEL Metrics API

### Counter (always increases)

```python
counter = meter.create_counter(
    name="operations_total",
    description="Total operations",
    unit="1"
)
counter.add(1, {"operation": "create"})  # Add with attributes (labels)
```

### UpDownCounter (gauge-like)

```python
gauge = meter.create_up_down_counter(
    name="active_connections",
    description="Current connections",
    unit="1"  
)
gauge.add(1)   # Increment
gauge.add(-1)  # Decrement
```

### Histogram (distributions)

```python
histogram = meter.create_histogram(
    name="request_duration_seconds",
    description="Request duration",
    unit="s"
)
histogram.record(0.25, {"endpoint": "/api"})  # Record observation
```

---

## Stop the Application

Press `Ctrl + C` in the terminal running `otel_app.py`.

---

**🌟 EXCELLENT! 🌟**

---

## Key Takeaways

You've learned:
- OpenTelemetry is a vendor-neutral observability SDK
- OTEL metrics export to Prometheus format automatically  
- OTEL uses similar concepts (counters, gauges, histograms)
- Same PromQL queries work with OTEL metrics
- OTEL enables multi-backend strategies

**When to use OTEL:**
- Building cloud-native microservices
- Need tracing AND metrics together
- Want flexibility to change backends
- Standardizing across multiple teams/languages

**When to use Prometheus client libraries:**
- Simple, Prometheus-only deployments
- Minimal dependencies preferred
- Existing Prometheus-specific tooling

---

**Next:** You can now instrument applications with both Prometheus and OpenTelemetry!
