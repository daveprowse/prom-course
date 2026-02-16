# ⚙️ Lab 11 - Instrumenting an Application

In this lab we will:

- Instrument a task queue processor application
- Use all four Prometheus metric types (counter, gauge, histogram, summary)
- Expose metrics and scrape them with Prometheus
- Query application metrics from the Web UI

## The Application

You'll instrument a simple task queue processor that:
- Receives tasks
- Processes them (simulated work)
- Tracks metrics about task processing

## Install Prerequisites

Make sure you have the Prometheus Python client library:

```bash
pip install prometheus-client
```

> Note: On Debian, use `--break-system-packages` flag if needed.
>
> Note: This lab uses port 8100 to avoid conflicts with the web server from Lab 10 (which uses port 8000).

---
### tmux

Consider using `tmux` or a similar multiplexing program so that you can split your terminal. 

To enable mouse support in tmux press `:` then 

```set -g mouse on
```
You can also add this to your `.tmux.conf` to make it permanent.

---

## The Application

Review the file called `task_processor.py`. This is your application that you will run.

If necessary, make the script executable:

```bash
chmod +x task_processor.py
```

## Run the Application

Execute the script:

```bash
python3 task_processor.py
```

You should see output like:
```
Metrics server started on :8100
Metrics available at http://localhost:8100/metrics
Processing task 1
Task 1 completed successfully in 0.87s
Processing task 2
Task 2 completed successfully in 1.23s
```

Let it run - it will process tasks continuously.

## Verify Metrics Endpoint

In another terminal, check that metrics are being exposed:

```bash
curl http://localhost:8100/metrics
```

You should see metrics like:
```
# HELP tasks_processed_total Total number of tasks processed
# TYPE tasks_processed_total counter
tasks_processed_total{status="success"} 15.0
tasks_processed_total{status="failed"} 2.0

# HELP tasks_active Number of tasks currently being processed
# TYPE tasks_active gauge
tasks_active 1.0

# HELP tasks_queue_size Number of tasks waiting in queue
# TYPE tasks_queue_size gauge
tasks_queue_size 23.0

# HELP task_duration_seconds Time spent processing tasks
# TYPE task_duration_seconds histogram
task_duration_seconds_bucket{le="0.1"} 0.0
task_duration_seconds_bucket{le="0.5"} 3.0
task_duration_seconds_bucket{le="1.0"} 8.0
...
```

## Configure Prometheus

Add the application to Prometheus scrape config.

Edit `/etc/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'task-processor'
    static_configs:
      - targets: ['localhost:8100']
```

> Note: Replace `localhost` with the IP address if running on a remote system.

Reload or Restart Prometheus:

```bash
sudo systemctl reload prometheus
```

## Query from Prometheus Web UI

Access the Prometheus Web UI at `http://localhost:9090`

### Query 1: Total Tasks Processed

```promql
tasks_processed_total
```

View in Table mode. You should see separate entries for `status="success"` and `status="failed"`.

### Query 2: Task Success Rate

```promql
sum(rate(tasks_processed_total{status="success"}[5m])) / sum(rate(tasks_processed_total[5m])) * 100
```

Shows percentage of successful tasks (should be around 90%).

### Query 3: Current Queue Size

```promql
tasks_queue_size
```

View in Graph mode. Should fluctuate between 5 and 50.

### Query 4: Task Processing Rate

```promql
rate(tasks_processed_total[1m])
```

Shows tasks **per second** (averaged over the last 1 minute).

> Note: `rate()` always returns per-second values. The `[1m]` is the lookback window for calculating the average. 

Try adjusting the time to 2m, 3m, etc...

> Note: To see the *total tasks per minute* try `increase(tasks_processed_total[1m])`.

### Query 5: 95th Percentile Task Duration

```promql
histogram_quantile(0.95, rate(task_duration_seconds_bucket[5m]))
```

95% of tasks complete within this time.

> Note: If your p95 value seems higher than expected (e.g., 4.5s when tasks max at 3.0s), this is due to histogram bucket interpolation. The buckets [0.1, 0.5, 1.0, 2.0, 5.0] have a large gap between 2.0 and 5.0. Prometheus linearly interpolates within that range. For more accurate percentiles, use finer-grained buckets like [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 5.0] in `task_processor.py`.

### Query 6: Average Task Duration

```promql
rate(task_duration_seconds_sum[5m]) / rate(task_duration_seconds_count[5m])
```

Mean task processing time.

### Query 7: Active Tasks

```promql
tasks_active
```

Should show 0 or 1 (one task at a time).

## Understanding the Metrics

**Counter (`tasks_processed_total`):**
- Only increases
- Tracks total tasks completed
- Use `rate()` to see tasks/second

**Gauge (`tasks_active`, `tasks_queue_size`):**
- Goes up and down
- Shows current state
- No rate calculation needed

**Histogram (`task_duration_seconds`):**
- Creates buckets automatically
- Use `histogram_quantile()` for percentiles
- Best for understanding distribution

**Summary (`task_latency_seconds`):**
- Similar to histogram
- Calculates quantiles client-side
- Less flexible than histograms

## Stop the Application

Press `Ctrl + C` in the terminal running `task_processor.py`.

---

👍 **Perfectamundo! You finished the lab!** 👍

---

## Key Takeaways

You've learned:
- How to instrument a real application
- Using all four metric types appropriately
- Exposing metrics via HTTP
- Querying custom application metrics
- Calculating success rates and percentiles

**Next:** Apply these patterns to your own applications!

---

## Extra Credit

### Challenge 1: Modify the Application

**Add new features:**

1. Add a new counter for `tasks_retried_total`
2. Change the success rate from 90% to 95%
3. Add a label for `task_type` (e.g., 'fast', 'slow', 'normal')
4. Create queries to compare task types

### Challenge 2: Create Alert Rules

Create an alert rule that fires when success rate drops below 85%.

Edit `/etc/prometheus/rules.yml`:

```yaml
groups:
  - name: task_processor_alerts
    rules:
      - alert: HighTaskFailureRate
        expr: |
          sum(rate(tasks_processed_total{status="failed"}[5m])) 
          / 
          sum(rate(tasks_processed_total[5m])) > 0.15
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Task processor failure rate above 15%"
          description: "Task processor has {{ $value | humanizePercentage }} failure rate"
      
      - alert: TaskProcessorDown
        expr: up{job="task-processor"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Task processor is down"
          description: "Task processor on {{ $labels.instance }} is not responding"
```

Make sure the `rule_files` section in `/etc/prometheus/prometheus.yml` points to your rules file:

```yaml
rule_files:
  - /etc/prometheus/rules.yml
```

Reload Prometheus:

```bash
sudo systemctl reload prometheus
```

### Challenge 3: PagerDuty Integration

Send critical alerts to PagerDuty when the task processor fails.

**Prerequisites:**
- PagerDuty account (free tier works)
- Integration key from Lab 08 (or create new one)

**1. Update Alertmanager configuration:**

Edit `/etc/alertmanager/alertmanager.yml`:

```yaml
route:
  receiver: 'default'
  routes:
    # Route critical alerts to PagerDuty
    - match:
        severity: critical
      receiver: 'pagerduty'
    # Route warnings to console (or another receiver)
    - match:
        severity: warning
      receiver: 'default'

receivers:
  - name: 'default'
    # Log to console only
    
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<your-pagerduty-integration-key>'
        description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'
```

> Note: Replace `<your-pagerduty-integration-key>` with your actual key from PagerDuty.

**2. Restart Alertmanager:**

```bash
sudo systemctl restart alertmanager
```

**3. Test the alert:**

Stop the task processor:

```bash
# Press Ctrl+C in the terminal running task_processor.py
```

Wait 1-2 minutes. You should receive a PagerDuty alert for "TaskProcessorDown".

**4. Test the high failure rate alert:**

Modify `task_processor.py` to reduce success rate to 70%:

```python
# Change this line:
if random.random() < 0.9:  # 90% success

# To this:
if random.random() < 0.7:  # 70% success (30% failure)
```

Restart the application and wait 5 minutes. You should see a warning in Prometheus Alerts (but NOT in PagerDuty since warnings don't route there).

**5. Verify in PagerDuty:**

- Log into PagerDuty
- Check Incidents tab
- You should see "TaskProcessorDown" incident
- Acknowledge or resolve it

**6. Clean up:**

Restart task processor with original 90% success rate:

```bash
python3 task_processor.py
```

The alert should auto-resolve in PagerDuty after 1-2 minutes.

---

**🚨 EXCELLENT! 🚨**

You've now integrated application monitoring with incident management!
