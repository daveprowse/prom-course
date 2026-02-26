# Sample Question #14 - Answer and Mini-Lab

## Question #14 (Prometheus Architecture)

A developer reports that a metric they just added to their application isn't appearing in Prometheus after 2 minutes. The application is running and exposing metrics on `/metrics`.

What is the FIRST thing you should check to troubleshoot this issue?

A) Check if the Prometheus TSDB has enough disk space

B) Verify the application is listed in the Prometheus scrape configuration and check the target status in the Prometheus UI

C) Restart the Prometheus server to reload the metrics

D) Check if the metric name follows Prometheus naming conventions

---

## Answer

**Answer:** B) Verify the application is listed in the Prometheus scrape configuration and check the target status in the Prometheus UI

**Explanation:** The most common reason for missing metrics is that Prometheus isn't scraping the target at all. Before investigating metric naming, storage, or other issues, you must verify that: (1) the target is configured in `prometheus.yml` under `scrape_configs`, and (2) the target shows as "UP" in Status → Targets. If the target isn't configured or is showing as "DOWN", Prometheus won't collect any metrics from it regardless of whether they're properly formatted.

**Incorrect Answers:**
- **A)** While disk space can cause issues, it's not the FIRST thing to check - Prometheus will log errors if it's out of space, and existing metrics would stop updating too
- **C)** Restarting Prometheus isn't necessary for new metrics from an existing target - Prometheus discovers new metrics automatically on each scrape
- **D)** Metric naming issues would show up in the Prometheus logs but wouldn't prevent ALL metrics from appearing - you'd likely see some metrics but not others

---

## Mini-Lab: Target Troubleshooting

**Objective:** Understand the scrape workflow and troubleshoot target issues

**Part 1 - Verify Existing Target (1 minute):**

1. Access Prometheus UI: `http://localhost:9090`
2. Go to **Status → Targets**
3. Find the `prometheus` job - it should show **UP**
4. Note the "Last Scrape" time and "Scrape Duration"

**Part 2 - Simulate Missing Target (2 minutes):**

1. Edit `/etc/prometheus/prometheus.yml`
2. Add a non-existent target:

```yaml
scrape_configs:
  - job_name: 'broken-app'
    static_configs:
      - targets: ['localhost:9999']  # Nothing running here
```

> Note: If scraping from a remote system, change `localhost` to the IP address of that system. 

3. Reload Prometheus: `sudo systemctl reload prometheus`
4. Check **Status → Targets** again
5. The `broken-app` job should show **DOWN** with an error message

**Part 3 - Fix and Verify (2 minutes):**

1. Start a simple metrics endpoint:

```bash
# In a new terminal
python3 -c "from prometheus_client import start_http_server; import time; start_http_server(9999); print('Metrics on :9999'); time.sleep(3600)"
```

> Note: You could also run a python script. If you prefer that, I've created one [below](#python-script).

2. Wait 15-30 seconds (for next scrape)
3. Refresh **Status → Targets**
4. The target should now show **UP**
5. Query: `python_info` - you should see the metric

**Cleanup:**
- Stop the Python server (Ctrl+C)
- Remove the `broken-app` job from prometheus.yml
- Reload Prometheus

**Key Takeaway:** Status → Targets is your first stop for troubleshooting. Always verify the target is UP before investigating metric-specific issues.

---
## Python Script 

```py
from prometheus_client import start_http_server
import time

start_http_server(9999)
print("Metrics server running on :9999")
print("Press Ctrl+C to stop")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopped")
```