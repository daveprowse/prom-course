# ⚙️ Testing Your SLO Alert (Extra Credit)

This optional exercise demonstrates how to actually trigger the SLO-based alert by generating real HTTP failures.

**Prerequisites:**
- Completed the SLO-Based Alerting mini-lab
- Python installed
- Basic understanding of HTTP status codes

**Time:** 10-15 minutes

---

## Overview

The main mini-lab showed you how SLO alerts work conceptually. Here, you'll:
1. Run a simple HTTP server that can generate failures
2. Configure Prometheus to scrape it
3. Generate errors to trigger the alert
4. Watch the burn rate spike and alert fire

---

## Step 1: Create the Test HTTP Server

We'll create a simple Python server that returns 200s normally but can be triggered to return 500s.

**Create a file called `test-server.py`:**

```python
#!/usr/bin/env python3
"""
Simple HTTP server for testing SLO alerts.
- GET / → returns 200 OK
- GET /fail → returns 500 Internal Server Error
- Metrics exposed on /metrics for Prometheus scraping
"""

import http.server
import socketserver
from urllib.parse import urlparse

# Counters for metrics
total_requests = 0
successful_requests = 0
failed_requests = 0

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global total_requests, successful_requests, failed_requests
        
        path = urlparse(self.path).path
        total_requests += 1
        
        # Metrics endpoint for Prometheus
        if path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            
            metrics = f"""# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{{status="200"}} {successful_requests}
http_requests_total{{status="500"}} {failed_requests}

# HELP http_requests_current Current request counts
# TYPE http_requests_current gauge
http_requests_current{{status="200"}} {successful_requests}
http_requests_current{{status="500"}} {failed_requests}
"""
            self.wfile.write(metrics.encode())
            return
        
        # Failure endpoint
        elif path == '/fail':
            failed_requests += 1
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Internal Server Error (intentional for testing)\n")
            return
        
        # Success endpoint (default)
        else:
            successful_requests += 1
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK - Test server is running\n")
            return
    
    def log_message(self, format, *args):
        # Suppress default logging to keep output clean
        pass

if __name__ == "__main__":
    PORT = 8089
    
    with socketserver.TCPServer(("", PORT), TestHandler) as httpd:
        print(f"Test server running on http://localhost:{PORT}")
        print(f"- Success endpoint: http://localhost:{PORT}/")
        print(f"- Failure endpoint: http://localhost:{PORT}/fail")
        print(f"- Metrics endpoint: http://localhost:{PORT}/metrics")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()
```

**Make it executable and run it:**

```bash
chmod +x test-server.py
python3 test-server.py
```

You should see:
```
Test server running on http://localhost:8089
- Success endpoint: http://localhost:8089/
- Failure endpoint: http://localhost:8089/fail
- Metrics endpoint: http://localhost:8089/metrics
Press Ctrl+C to stop
```

**Test the server:**

In another terminal:

```bash
# Generate successful requests
curl http://localhost:8089/
# Returns: OK - Test server is running

# Generate failed requests
curl http://localhost:8089/fail
# Returns: Internal Server Error (intentional for testing)

# Check metrics
curl http://localhost:8089/metrics
# Shows counters for both 200 and 500 responses
```

---

## Step 2: Configure Prometheus to Scrape the Test Server

**Edit `/etc/prometheus/prometheus.yml`:**

Add a new job:

```yaml
  - job_name: 'test-server'
    static_configs:
      - targets:
        - 'localhost:8089'
    scrape_interval: 5s
```

> Note: 5s scrape interval for faster testing feedback

**Restart Prometheus:**

```bash
sudo systemctl restart prometheus
```

**Verify scraping:**

Prometheus UI → Status → Targets

Look for `test-server` job - should show as "UP"

Query:
```promql
http_requests_total
```

Should show metrics from your test server.

---

## Step 3: Create SLI Rule for Test Server

**Edit `/etc/prometheus/rules/slo.yml`:**

Add a second recording rule for the test server:

```yaml
groups:
  - name: slo
    interval: 30s
    rules:
      # Existing Prometheus SLI
      - record: http:availability:sli
        expr: |
          sum(rate(prometheus_http_requests_total{code=~"2.."}[5m]))
          /
          sum(rate(prometheus_http_requests_total[5m]))
      
      # NEW: Test server SLI
      - record: test:availability:sli
        expr: |
          sum(rate(http_requests_total{status="200"}[5m]))
          /
          sum(rate(http_requests_total[5m]))

  - name: slo_alerts
    rules:
      # Existing alert for Prometheus
      - alert: HighErrorBudgetBurn
        expr: (1 - http:availability:sli) / (1 - 0.999) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Burning error budget 10x faster than sustainable"
      
      # NEW: Alert for test server
      - alert: TestServerErrorBudgetBurn
        expr: (1 - test:availability:sli) / (1 - 0.999) > 10
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Test server burning error budget 10x faster than sustainable"
```

**Note:** Reduced `for` duration to 2m for faster testing.

**Reload Prometheus:**

```bash
sudo systemctl restart prometheus
```

**Verify:**

Query:
```promql
test:availability:sli
```

Should return `1` (100% availability).

---

## Step 4: Generate Normal Traffic (Baseline)

Generate some normal successful requests:

```bash
for i in {1..100}; do
  curl -s http://localhost:8089/ > /dev/null
  sleep 0.1
done
```

**Check the SLI:**

```promql
test:availability:sli
```

Should still be `1` (or very close).

**Check burn rate:**

```promql
(1 - test:availability:sli) / (1 - 0.999)
```

Should be `0` or very close to 0.

---

## Step 5: Generate Failures and Watch Alert Fire

Now generate a burst of failures to drop availability below SLO:

```bash
# Generate 500 failed requests rapidly
for i in {1..500}; do
  curl -s http://localhost:8089/fail > /dev/null
done
```

**Immediately watch the metrics:**

**1. Check availability dropping:**

```promql
test:availability:sli
```

Should drop significantly (maybe to 0.8-0.9 or lower).

**2. Check burn rate spiking:**

```promql
(1 - test:availability:sli) / (1 - 0.999)
```

Should spike well above 10!

For example:
- If SLI drops to 0.90 (90% success rate)
- Error rate: `1 - 0.90 = 0.10` (10% failures)
- Burn rate: `0.10 / 0.001 = 100` 🔥

**3. Watch the alert:**

Prometheus UI → **Alerts** → Find `TestServerErrorBudgetBurn`

- Should turn **yellow** (pending) immediately
- After 2 minutes, turns **red** (firing)

**Success!** You've triggered an SLO-based alert.

---

## Step 6: Recovery

Generate more successful requests to recover:

```bash
for i in {1..1000}; do
  curl -s http://localhost:8089/ > /dev/null
done
```

**Watch metrics recover:**

```promql
test:availability:sli
```

Should climb back toward 1.

```promql
(1 - test:availability:sli) / (1 - 0.999)
```

Should drop back below 10.

**Alert resolves:**

After burn rate stays below threshold for 2+ minutes, alert clears (turns green).

---

## Understanding What You've Demonstrated

**The burn rate concept in action:**

| Scenario | SLI | Error Rate | Burn Rate | Alert? |
|----------|-----|------------|-----------|--------|
| Normal ops | 0.999 | 0.1% | 1x | ✅ No |
| Slight issues | 0.995 | 0.5% | 5x | ✅ No |
| **Problem** | 0.990 | 1.0% | **10x** | ⚠️ **YES** |
| **Outage** | 0.900 | 10% | **100x** | 🔥 **YES** |

**What the 10x burn rate means:**
- At this rate, you'll exhaust your monthly error budget in 3 days
- This is the threshold where you need to investigate
- Higher burn rates = more urgent response needed

---

## Clean Up

**Stop the test server:**

Press `Ctrl+C` in the terminal running `test-server.py`

**Remove test server from Prometheus (optional):**

Edit `prometheus.yml` and remove or comment out the `test-server` job:

```yaml
  # - job_name: 'test-server'
  #   static_configs:
  #     - targets:
  #       - 'localhost:8089'
  #   scrape_interval: 5s
```

**Remove test alerts (optional):**

Edit `/etc/prometheus/rules/slo.yml` and remove or comment out the test server rules.

**Restart Prometheus:**

```bash
sudo systemctl restart prometheus
```

---

## Key Takeaways

**What you learned:**
1. ✅ How to generate realistic HTTP failures for testing
2. ✅ How SLIs respond to availability changes in real-time
3. ✅ How burn rates spike during incidents
4. ✅ How SLO alerts fire when error budget is consumed too fast
5. ✅ The relationship between error rate and burn rate

**Why this matters:**
- In production, you'd see this pattern during real incidents
- The alert gives you early warning before SLA breach
- Burn rate thresholds determine response urgency
- You can set multiple burn rate thresholds for different severity levels

**Production differences:**
- Multiple time windows (fast detection + reduced false positives)
- Integration with Alertmanager for notifications
- Runbooks linked to alerts
- Dashboard showing error budget consumption over time

---

## Extra Credit Extensions

**1. Experiment with different burn rates:**

Try generating different failure ratios and calculate the burn rates:
- 1% error rate → 10x burn rate (triggers alert)
- 5% error rate → 50x burn rate (critical!)
- 0.5% error rate → 5x burn rate (elevated but no alert)

**2. Multi-window burn rate alerts:**

Modify the alert to require BOTH short and long windows:

```yaml
      - alert: TestServerErrorBudgetBurn
        expr: |
          (
            (1 - test:availability:sli) / (1 - 0.999) > 10
          )
          and
          (
            (1 - avg_over_time(test:availability:sli[1h])) / (1 - 0.999) > 10
          )
        for: 2m
```

This reduces false positives from temporary spikes.

**3. Create a Grafana dashboard:**

Visualize:
- Current SLI value
- Burn rate over time
- Error budget remaining
- Alert status

**4. Modify the SLO:**

Change from 99.9% to 99.5% and recalculate burn rates. How does it affect alerting?

---

**Congratulations!** You've successfully tested SLO-based alerting end-to-end. This is exactly how modern teams monitor service reliability.
