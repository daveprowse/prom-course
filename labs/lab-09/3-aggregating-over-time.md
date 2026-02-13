# Aggregating over Time

**Aggregating over Time**: This is when you calculate summary statistics (average, max, min) across a time range rather than at a single moment. Functions like `avg_over_time()` and `max_over_time()` analyze how metrics behave over periods, smoothing out spikes and revealing trends.

Time-based aggregations show trends and patterns.

**1. Average over time:**

```
avg_over_time(up[5m])
```

Average uptime over last 5 minutes. 

This can be useful for flapping services. For example if our SSH service was only working 80% of the time:

```
avg_over_time(node_systemd_unit_state{name="ssh.service", state="active", job="remote-systems"}[10m])
```

> Note: Replace my IP address with yours. Also, use `sshd` if necessary on your distribution of Linux.

**2. Maximum over time:**

```
max_over_time(prometheus_http_request_duration_seconds_sum[1h])
```

Peak request duration in last hour.

**3. Minimum over time:**

```
min_over_time(process_resident_memory_bytes[10m])
```

Lowest memory usage in last 10 minutes.

**4. Count over time:**

```
count_over_time(up[5m])
```

Number of samples collected. This should show a sampling rate of once per 15 seconds (normally).

## Prediction

**Prediction**: Uses historical time-series data to forecast future values. `predict_linear()` analyzes trends over a time range to extrapolate when thresholds will be reached - crucial for capacity planning and proactive alerting.

Predict future values:

```
predict_linear(process_resident_memory_bytes[1h], 3600)
```

Predicts memory usage 1 hour from now based on last hour's trend.

Now, let's try one that will predict bytes available on a disk (in GB) in 4 hours from now:

```
predict_linear(node_filesystem_avail_bytes{mountpoint="/",job="remote-systems"}[1h], 4*3600) / 1024 / 1024 / 1024
```

**Components of that query:**

- `predict_linear()` - Function that forecasts future values based on linear regression
- `node_filesystem_avail_bytes` - Metric measuring available disk space in bytes
- `{mountpoint="/",job="remote-systems"}` - Selects the root filesystem on remote systems
- `[1h]` - Analyzes the last 1 hour of data to establish the trend
- `4*3600` - Projects 4 hours into the future (4 hours × 3600 seconds/hour = 14,400 seconds)
- `/ 1024 / 1024 / 1024` - Converts bytes to gigabytes (divide by 1024 three times: bytes → KB → MB → GB)

**Result:** Predicted available disk space in GB on the root filesystem 4 hours from now, based on the trend over the past hour.

> Note about delimters: Parentheses `()` follow the function. They will incorporate the metric to be queried. Curlybraces `{}` surround the labels. And square brackets `[]` surround time ranges.

Remember: *Time-based aggregations* reveal trends and patterns by analyzing metric behavior over windows of time. This is essential for understanding system performance and predicting future issues.
