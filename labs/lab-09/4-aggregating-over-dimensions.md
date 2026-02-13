# Aggregating over Dimensions

Aggregate across label dimensions to summarize data. The label dimensions might include: `job=x` and `instance=x`.

**1. Sum across all instances:**

```
sum(up)
```

Total number of targets currently up.

Or try this to see the sum of all http requests:

```
sum (prometheus_http_requests_total)
```

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

`topk` is a great way to filter the most common counts, especially if you have a long list.

```
topk(3, prometheus_http_requests_total)
```

Top 3 highest request counts.

## From CLI

Get aggregated data with `curl`:

```bash
curl 'http://localhost:9090/api/v1/query?query=sum(up)' | jq
```
