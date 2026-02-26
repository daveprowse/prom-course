# Sample Question #15 - Answer and Mini-Lab

## Question #15 (Instrumentation)

You're instrumenting a payment processing system and need to track the time it takes to process each payment. You want to be able to calculate percentiles (p50, p95, p99) and identify slow transactions.

Which metric type should you use, and what would be the correct Python code?

A) **Counter** - `payment_duration = Counter('payment_duration_seconds', 'Payment duration')`

B) **Gauge** - `payment_duration = Gauge('payment_duration_seconds', 'Payment duration')`

C) **Histogram** - `payment_duration = Histogram('payment_duration_seconds', 'Payment duration')`

D) **Summary** - `payment_duration = Summary('payment_duration_seconds', 'Payment duration')`

---

## Answer

**Answer:** C) **Histogram** - `payment_duration = Histogram('payment_duration_seconds', 'Payment duration')`

**Explanation:** Histogram is the correct choice for tracking durations when you need to calculate percentiles. Histograms automatically create buckets that group observations by duration ranges, allowing Prometheus to calculate percentiles using `histogram_quantile()`. Histograms are also more efficient for high-cardinality scenarios and work well with Prometheus's aggregation model. They're specifically designed for measuring request durations, response sizes, and similar distributed values.

**Incorrect Answers:**
- **A) Counter** - Only increases, never decreases. Used for counting events (total requests, errors), not measuring durations
- **B) Gauge** - Can go up and down but stores only the current value, not a distribution. You'd lose historical duration data and couldn't calculate percentiles
- **D) Summary** - While Summary can calculate percentiles, it does so on the client side and the pre-calculated percentiles can't be aggregated across instances. Histograms are preferred in Prometheus because they can be aggregated

---

## Mini-Lab: Histogram Instrumentation

**Objective:** Add histogram instrumentation and calculate percentiles

**Part 1 - Create Instrumented Script (3 minutes):**

Create `payment_processor.py`:

```python
#!/usr/bin/env python3
from prometheus_client import Histogram, Counter, start_http_server
import time
import random

# Define metrics
payment_duration = Histogram(
    'payment_duration_seconds',
    'Time to process payment',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]  # Custom buckets
)

payments_total = Counter(
    'payments_processed_total',
    'Total payments processed',
    ['status']  # Label for success/failure
)

def process_payment():
    """Simulate payment processing"""
    # Measure duration
    start = time.time()
    
    # Simulate work (random duration)
    duration = random.uniform(0.1, 3.0)
    time.sleep(duration)
    
    # Record duration in histogram
    payment_duration.observe(duration)
    
    # Determine success/failure (90% success rate)
    if random.random() < 0.9:
        payments_total.labels(status='success').inc()
        status = 'SUCCESS'
    else:
        payments_total.labels(status='failure').inc()
        status = 'FAILED'
    
    print(f"Payment processed: {duration:.2f}s - {status}")

if __name__ == '__main__':
    # Start metrics server
    start_http_server(8300)
    print("Payment processor started on :8300")
    print("Metrics: http://localhost:8300/metrics\n")
    
    # Process payments continuously
    while True:
        process_payment()
        time.sleep(1)  # Wait 1 second between payments
```

Make it executable and run it:
```bash
chmod +x payment_processor.py
python3 payment_processor.py
```

> Note: We have used a lot of ports so far. If you have any conflicts, simply change the port # (8300) to an unused number. For a list of all ports we have used, see the [port reference](../../port-reference.md) document.

**Part 2 - Configure Prometheus (1 minute):**

Edit `/etc/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'payment-processor'
    static_configs:
      - targets: ['localhost:8300']
```

> Note: If scraping from a remote system, change `localhost` to the IP address of that system. 

Our `prometheus.yml` is getting fairly busy, so run a check on it:

```bash
sudo promtool check config /etc/prometheus/prometheus.yml
```

Reload Prometheus: `sudo systemctl reload prometheus`

**Part 3 - Query Histogram Data (3 minutes):**

In Prometheus UI, run these queries:

**1. View raw buckets:**
```promql
payment_duration_seconds_bucket
```

**2. Calculate p50 (median):**
```promql
histogram_quantile(0.5, rate(payment_duration_seconds_bucket[1m]))
```

**3. Calculate p95:**
```promql
histogram_quantile(0.95, rate(payment_duration_seconds_bucket[1m]))
```

**4. Calculate p99:**
```promql
histogram_quantile(0.99, rate(payment_duration_seconds_bucket[1m]))
```

---
**Understanding Percentiles (P50, P95, P99):**

Percentiles tell you what value X% of observations fall below:

- **P50 (median)**: 50% of payments process faster than this time
  - Example: P50 = 1.5s means half your payments complete in under 1.5 seconds
  - Good for understanding "typical" performance

- **P95**: 95% of payments process faster than this time (only 5% are slower)
  - Example: P95 = 2.8s means 95 out of 100 payments complete in under 2.8 seconds
  - Good for understanding "most" customer experiences
  - Common SLO target: "P95 latency < 3 seconds"

- **P99**: 99% of payments process faster than this time (only 1% are slower)
  - Example: P99 = 4.2s means only 1 in 100 payments takes longer than 4.2 seconds
  - Catches outliers and worst-case scenarios
  - Important for identifying performance problems

**Why all three matter:**
- P50 alone can hide problems (average might be fast while many users suffer)
- P95 shows what most users experience (not just the lucky half)
- P99 catches the "long tail" - rare but painful slow requests

**Real-world example:** If your P50 is 0.5s but P99 is 30s, that means most payments are fast but 1% of customers wait half a minute - unacceptable for production!

---


**5. Average duration:**
```promql
rate(payment_duration_seconds_sum[1m]) / rate(payment_duration_seconds_count[1m])
```

**6. Payment success rate:**
```promql
sum(rate(payments_processed_total{status="success"}[1m])) 
/ 
sum(rate(payments_processed_total[1m])) * 100
```

**Part 4 - Observe the Distribution (2 minutes):**

1. Let it run for 2-3 minutes to collect data
2. Run the percentile queries above
3. Notice:
   - p50 (median) is around 1.5 seconds
   - p95 shows slower transactions
   - p99 catches the slowest 1%

**Cleanup:**
- Stop the payment processor (Ctrl+C)
- Remove the job from prometheus.yml
- Reload Prometheus

**Key Takeaways:**
- Histograms create `_bucket`, `_sum`, and `_count` metrics automatically
- Use `histogram_quantile()` to calculate any percentile
- Histograms are essential for SLOs and performance monitoring
- Custom buckets should match your expected distribution

**This mini-lab tied together a lot of important Prometheus concepts:**

- ✅ Metric type selection (why histogram for durations)
- ✅ Client library usage (proper instrumentation patterns)
- ✅ Histogram mechanics (_bucket, _sum, _count suffixes)
- ✅ PromQL functions (histogram_quantile, rate)
- ✅ Percentiles (P50, P95, P99 and what they mean)
- ✅ Real-world application (payment processing SLOs)

---

## 🥳 YOU'VE REACHED THE END!

That was the last mini-lab, and the end of this video course. 🏁🏁 

I sincerely hope you gained experience with Prometheus and enjoyed the course. Go out there and dominate!

Dave Prowse

https://prowse.tech