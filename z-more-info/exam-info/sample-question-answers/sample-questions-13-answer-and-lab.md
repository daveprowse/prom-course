# Sample Question #13 - Answer and Mini-Lab

## Question #13 (PromQL)

You need to create an alert that fires when your service's error rate exceeds 5% over the last 5 minutes. Your application exposes a counter metric `http_requests_total` with a `status` label (values: "success", "error").

Which PromQL expression correctly calculates this error rate?

A) `sum(rate(http_requests_total{status="error"}[5m])) > 0.05`

B) `rate(http_requests_total{status="error"}[5m]) / rate(http_requests_total[5m]) > 0.05`

C) `sum(rate(http_requests_total{status="error"}[5m])) / sum(rate(http_requests_total[5m])) > 0.05`

D) `increase(http_requests_total{status="error"}[5m]) / http_requests_total > 0.05`

---

## Answer

**Answer:** C) `sum(rate(http_requests_total{status="error"}[5m])) / sum(rate(http_requests_total[5m])) > 0.05`

**Explanation:** To calculate an error rate percentage, you need to divide the rate of errors by the rate of all requests. The `sum()` aggregation is crucial because `rate()` returns a per-time-series rate, and you likely have multiple instances or labels. By summing first, you get the total error rate across all series divided by the total request rate across all series. This gives you the overall error rate as a decimal (0.05 = 5%).

**Incorrect Answers:**
- **A)** Missing the division by total requests - this just checks if there are any errors at all (> 0.05 requests/second), not the error rate percentage
- **B)** Divides individual time series before aggregation, which doesn't give you the overall error rate across all instances
- **D)** Uses `increase()` without `rate()` and compares against the raw counter value, which doesn't calculate a rate or percentage correctly

---

## Mini-Lab: Error Rate Calculation

**Objective:** Test error rate calculations with multiple instances to see aggregation differences

**Setup (3 minutes):**

Create a simple test script `api_simulator.py`:

```python
#!/usr/bin/env python3
from prometheus_client import Counter, start_http_server
import time
import random

# API request counter with status label
api_requests = Counter('api_requests_total', 'API requests', ['instance', 'status'])

# Simulate 3 instances with different error rates
instances = {
    'api-1': 0.05,  # 5% errors
    'api-2': 0.15,  # 15% errors
    'api-3': 0.02,  # 2% errors
}

if __name__ == '__main__':
    start_http_server(8350)
    print("API Simulator on :8350/metrics\n")
    
    while True:
        for instance, error_rate in instances.items():
            # Generate success or error
            if random.random() < error_rate:
                api_requests.labels(instance=instance, status='error').inc()
                print(f"{instance}: ERROR")
            else:
                api_requests.labels(instance=instance, status='success').inc()
                print(f"{instance}: success")
        time.sleep(2)
```

Run it:
```bash
chmod +x api_simulator.py
python3 api_simulator.py
```

Configure the Prometheus server (`/etc/prometheus/prometheus.yml`):
```yaml
  - job_name: 'api-sim'
    static_configs:
      - targets: ['localhost:8350']
```

> Note: If using a secondary system, change `localhost` to the IP address of the remote system.

Reload: `sudo systemctl reload prometheus`

Wait 1-2 minutes for data.

**Compare Query Methods (3 minutes):**

**Method A (RIGHT) - Per-instance rates (3 separate values):**
```promql
sum by(exported_instance) (rate(api_requests_total{status="error"}[1m])) 
/ 
sum by(exported_instance) (rate(api_requests_total[1m]))
```
Result: Shows 3 lines - one per instance (api-1: ~0.05, api-2: ~0.15, api-3: ~0.02)

**Method B (RIGHT) - Overall aggregated rate (1 value):**
```promql
sum(rate(api_requests_total{status="error"}[1m])) / sum(rate(api_requests_total[1m]))
```
Result: Shows single value - weighted average across all instances (~0.073 or 7.3%)

---
**The Key Difference:**
- Method A: Useful for identifying which instance has issues
- Method B: Useful for overall system health and alerting
- For alerts checking "is my service degraded?", you need Method B
---

**Method C - WRONG: What happens without proper aggregation:**
```promql
rate(api_requests_total{status="error"}[1m]) / rate(api_requests_total[1m])
```

**Result: Garbage!** Returns something like `1, NaN, NaN`

**Why it fails:**
- Prometheus tries to divide time series by matching ALL labels
- Left side: `{exported_instance="api-1", status="error"}`
- Right side has TWO series: `{exported_instance="api-1", status="error"}` AND `{exported_instance="api-1", status="success"}`
- No exact match found → NaN
- Occasionally one might match by coincidence → returns 1 (meaningless)

**The lesson:** You MUST aggregate away the `status` label with `sum()` before dividing, otherwise Prometheus can't match the time series correctly. This is why Methods A and B use `sum()` - it removes conflicting labels and allows proper division.

**Cleanup:**
- Stop script (Ctrl+C)
- Remove from prometheus.yml
- Reload Prometheus

**Key Takeaway:** Aggregation with `sum()` before division gives you the fleet-wide error rate, not individual instance rates. This is critical for SLO-based alerting.
