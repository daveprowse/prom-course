# Rates and Derivatives

Rates calculate change over time. Essential for counter metrics.

## Understanding Counters

Counters only increase (except on reset). Raw values aren't useful - we need rates.

**1. View raw counter:**

```
prometheus_http_requests_total{code="200"}
```

Large numbers that keep growing.

**2. Calculate rate (per-second average):**

**Derivative**: The rate of change of a value over time. In PromQL, functions like `rate()` and `irate()` calculate derivatives by measuring how quickly a counter is increasing, giving you the speed of change rather than the raw total.

Try this one:

```
rate(prometheus_http_requests_total{code="200"}[5m])
```

Shows requests per second over last 5 minutes.

**3. Instant rate:**

```
irate(prometheus_http_requests_total{code="200"}[5m])
```

Uses only last two samples. More sensitive to spikes.

**4. Total increase:**

```
increase(prometheus_http_requests_total{code="200"}[1h])
```

Total requests in last hour.

## Generate Load

Create some traffic:

```bash
for i in {1..100}; do curl http://localhost:9090/metrics > /dev/null 2>&1; done
```

Re-run the rate query - you'll see increased values. It will be easier to visaulize in Graph mode.

Rates are essential for monitoring - they transform ever-increasing counters into meaningful per-second metrics that show actual system activity.
