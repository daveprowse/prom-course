# Histograms

## Histograms in Prometheus:

Histograms track the distribution of values by counting observations in predefined buckets. Instead of recording every individual value, they group measurements into ranges.

**Why use them:**

- **Track latency/response times**: See how many requests completed in <100ms, <500ms, <1s, etc.
- **Calculate percentiles**: Answer "95% of requests finish within X seconds"
- **Measure request/response sizes**: Distribution of payload sizes
- **Low overhead**: More efficient than recording every single value
- **Identify outliers**: Spot slow requests or unusual patterns

**Example use case:**
Instead of storing 10,000 individual response times, histogram buckets show:

- 5,000 requests < 100ms
- 3,000 requests < 500ms
- 1,500 requests < 1s
- 500 requests > 1s

This lets you calculate "95% of requests complete in under 500ms" without storing every individual measurement.

**Bottom line**: Histograms efficiently track performance distributions, essential for SLOs and understanding system behavior.

## Understanding Histogram Metrics

Histograms create multiple time series:
- `_bucket{le="x"}`: Count of observations ≤ x
- `_sum`: Sum of all observations
- `_count`: Total number of observations

**1. View histogram buckets:**

```
prometheus_http_request_duration_seconds_bucket
```

Shows buckets for different latency thresholds.

> Note: To better visualize this, add this query in Grafana as a new query (in a new panel) and change the visualization type to Histogram.

**2. Calculate average latency:**

```
rate(prometheus_http_request_duration_seconds_sum[5m]) / rate(prometheus_http_request_duration_seconds_count[5m])
```

**3. 95th percentile:**

```
histogram_quantile(0.95, rate(prometheus_http_request_duration_seconds_bucket[5m]))
```

95% of requests complete within this time.

**4. 50th percentile (median):**

```
histogram_quantile(0.50, rate(prometheus_http_request_duration_seconds_bucket[5m]))
```

## Generate Traffic for Better Data

```bash
for i in {1..1000}; do curl http://localhost:9090/api/v1/query?query=up > /dev/null 2>&1; done
```

Wait 15 seconds, then re-run histogram queries to see distribution.

> Note: You might consider changing the scrape interval in `/etc/prometheus/prometheus.yml`. Be careful with this, the default is good for most use cases, but you might see 5s in some high-priority scenarios that need quick alerting. A decently powered VM should be able to do this if you want to speed up your responses. Conversely, you might see 30s-60s for lower priority scenarios. Warning: Never go below 1 second as it could crash Prometheus!
