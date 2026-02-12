# ⚙️ Lab 09 - PromQL

In this lab we will explore PromQL through hands-on exercises.

Each part is a short, focused sub-lesson on a specific PromQL concept.

---

## Part 1 - Selecting Data

PromQL selects time series data using metric names and label matchers.

### Basic Selection

Access the Prometheus Web UI and run these queries:

**1. Select all Prometheus metrics:**

```
prometheus_http_requests_total
```

View in Table mode. Each row is a unique time series with different labels. Note the *code* label.

**2. Filter by label (exact match):**

```
prometheus_http_requests_total{code="200"}
```

Shows only successful requests. 

Note: View all the HTTP status codes [here](../../z-more-info/promql-docs/http-status-codes.md).

**3. Filter by multiple labels:**

```
prometheus_http_requests_total{code="200",handler="/metrics"}
```

**4. Regex matching:**

```
prometheus_http_requests_total{handler=~"/api.*"}
```

Matches any handler starting with `/api`.

> Note: Regex (regular expression) is a sequence of characters that forms a search pattern. Used with test strings.

**5. Negative matching:**

```
up{job!="prometheus"}
```

Shows all jobs except Prometheus.

- Available arithmetic operators:

    `+`, `-`, `*`, `/`, `%`, `^`

- Available comparison operators:

    `==`, `!=`, `>`, `<`, `>=`, `<=`

- Available logical operators:

    `and`, `or`, `unless`

> Note: For more information on PromQL operators, see [this link](../../z-more-info/promql-docs/promql-operators.md).

### From CLI

Query from command line:

```bash
curl 'http://localhost:9090/api/v1/query?query=up'
```

Try a couple of other queries in the place of `up`. Also, pipe to jq (` | jq`) for easier reading!

---

## Part 2 - Rates and Derivatives

Rates calculate change over time. Essential for counter metrics.

### Understanding Counters

Counters only increase (except on reset). Raw values aren't useful - we need rates.

**1. View raw counter:**

```
prometheus_http_requests_total{code="200"}
```

Large numbers that keep growing.

**2. Calculate rate (per-second average):**

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

### Generate Load

Create some traffic:

```bash
for i in {1..100}; do curl http://localhost:9090/metrics > /dev/null 2>&1; done
```

Re-run the rate query - you'll see increased values. It will be easier to visaulize in Graph mode.

---

## Part 3 - Aggregating over Time

Time-based aggregations show trends and patterns.

**1. Average over time:**

```
avg_over_time(up[5m])
```

Average uptime over last 5 minutes (useful for flapping services).

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

Number of samples collected.

### Prediction

Predict future values:

```
predict_linear(process_resident_memory_bytes[1h], 3600)
```

Predicts memory usage 1 hour from now based on last hour's trend.

---

## Part 4 - Aggregating over Dimensions

Aggregate across label dimensions to summarize data.

**1. Sum across all instances:**

```
sum(up)
```

Total number of targets currently up.

**2. Count by job:**

```
count by(job) (up)
```

Number of targets per job.

**3. Average by instance:**

```
avg by(instance) (rate(prometheus_http_requests_total[5m]))
```

Average request rate per instance.

**4. Sum without specific labels:**

```
sum without(code) (prometheus_http_requests_total)
```

Removes the `code` label dimension, summing across all codes.

**5. Top K values:**

```
topk(3, prometheus_http_requests_total)
```

Top 3 highest request counts.

### From CLI

Get aggregated data:

```bash
curl 'http://localhost:9090/api/v1/query?query=sum(up)' | jq
```

---

## Part 5 - Binary Operators

Combine metrics with arithmetic and comparison operators.

### Arithmetic

**1. Calculate percentage:**

```
(process_resident_memory_bytes / 1024 / 1024)
```

Convert bytes to megabytes.

**2. Ratio:**

```
rate(prometheus_http_requests_total{code="200"}[5m]) / rate(prometheus_http_requests_total[5m])
```

Success rate percentage.

**3. Addition:**

```
up + 1
```

Adds 1 to each value.

### Comparison

**4. Filter by threshold:**

```
up > 0
```

Returns only targets that are up (filters out zeros).

**5. Equality check:**

```
up == 1
```

Returns only values equal to 1.

### Logical Operators

**6. AND condition:**

```
up == 1 and process_resident_memory_bytes > 50000000
```

Targets that are up AND using >50MB memory.

---

## Part 6 - Histograms

Histograms track value distributions (latency, request sizes).

### Understanding Histogram Metrics

Histograms create multiple time series:
- `_bucket{le="x"}`: Count of observations ≤ x
- `_sum`: Sum of all observations
- `_count`: Total number of observations

**1. View histogram buckets:**

```
prometheus_http_request_duration_seconds_bucket
```

Shows buckets for different latency thresholds.

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

### Generate Traffic for Better Data

```bash
for i in {1..1000}; do curl http://localhost:9090/api/v1/query?query=up > /dev/null 2>&1; done
```

Re-run histogram queries to see distribution.

---

## Part 7 - Timestamp Metrics

Work with time and timestamps in queries.

**1. Current timestamp:**

```
time()
```

Returns current Unix timestamp.

**2. Day of week:**

```
day_of_week()
```

Returns 0-6 (Sunday-Saturday).

**3. Hour of day:**

```
hour()
```

Returns 0-23.

**4. Time-based filtering:**

```
up and hour() > 9 and hour() < 17
```

Show uptime only during business hours (9 AM - 5 PM).

**5. Timestamp of sample:**

```
timestamp(up)
```

Shows when each sample was collected.

### From CLI

Check current time:

```bash
curl 'http://localhost:9090/api/v1/query?query=time()' | jq
```

---

## Part 8 - PromQL: Tying it All Together

Combine concepts into real-world queries.

### Scenario 1: Service Health Dashboard

**Calculate request success rate:**

```
sum(rate(prometheus_http_requests_total{code=~"2.."}[5m])) / sum(rate(prometheus_http_requests_total[5m])) * 100
```

Percentage of successful (2xx) requests.

### Scenario 2: Resource Monitoring

**Memory usage percentage:**

```
process_resident_memory_bytes / 1024 / 1024
```

Current memory in MB.

**Predict memory exhaustion:**

```
predict_linear(process_resident_memory_bytes[30m], 3600) > 500000000
```

Alert if memory will exceed 500MB in next hour.

### Scenario 3: Performance Analysis

**Request rate by handler:**

```
sum by(handler) (rate(prometheus_http_requests_total[5m]))
```

**95th percentile latency:**

```
histogram_quantile(0.95, sum by(le) (rate(prometheus_http_request_duration_seconds_bucket[5m])))
```

### Scenario 4: Capacity Planning

**Requests per hour trend:**

```
increase(prometheus_http_requests_total[1h])
```

**Top 3 busiest endpoints:**

```
topk(3, sum by(handler) (rate(prometheus_http_requests_total[5m])))
```

### Export Query Results

Save query results to file:

```bash
curl 'http://localhost:9090/api/v1/query?query=up' | jq '.data.result' > results.json
```

View the file:

```bash
cat results.json
```

---

**🏆 YOU DID IT! 🏆**

---

## Summary

You've learned:
- **Selecting**: Filter time series with label matchers
- **Rates**: Calculate change over time for counters
- **Time Aggregation**: Trends with avg_over_time, predict_linear
- **Dimension Aggregation**: Sum, count, avg across labels
- **Operators**: Arithmetic, comparison, logical operations
- **Histograms**: Percentiles and distributions
- **Timestamps**: Time-based queries and filters
- **Real-World**: Combined queries for monitoring and alerting

PromQL is now in your toolkit for Prometheus monitoring!

Remember. You are awesome!