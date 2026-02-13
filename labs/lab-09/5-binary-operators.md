# Binary Operators

Binary operators combine metrics with arithmetic and comparison operators.

Let's show some examples of binary operators in Prometheus queries. 

> Note: For more information about all of the binary operators you can use, see [this link](../../z-more-info/promql-docs/promql-operators.md).

## Arithmetic

**1. Calculate percentage:**

```
(process_resident_memory_bytes / 1024 / 1024)
```

Convert bytes to megabytes.

**2. Addition:**

```
up + 1
```

Adds 1 to each value.

## Comparison

**3. Filter by threshold:**

```
up > 0
```

Returns only targets that are up (filters out zeros).

**4. Equality check:**

```
up == 1
```

Returns only values equal to 1.

## Logical Operators

**5. AND condition:**

```
up == 1 and process_resident_memory_bytes > 50000000
```

Targets that are up AND using >50MB memory. This should exclude the remote system with the node_exporter installed because that is usally around 25 MB usage. However, it should display the Prometheus server because that is usually above 80 MB. Change it to 20 MB (20000000 or more accurately 20971520) to have the other system with node_exporter display as well. 

**6. OR condition:**
```promql
up == 0 or process_resident_memory_bytes > 100000000
```

Targets that are down OR using >100MB memory (either condition triggers result).

**7. UNLESS condition:**
```promql
up unless process_resident_memory_bytes > 100000000
```

Shows all targets EXCEPT those using >100MB memory (excludes matching results).

## Next LEVEL!

**8. Traffic distribution (as percentage):**

Generate mixed traffic across different endpoints to see a realistic percentage of a single handler. 

We'll create traffic on three handlers using three separate for loops. Then, we'll query against the `/metrics` handler to find out what percentage of traffic it is getting. 

```bash
# Hit /metrics endpoint
for i in {1..50}; do 
  curl 'http://localhost:9090/metrics' > /dev/null 2>&1
done

# Hit /api/v1/query endpoint
for i in {1..100}; do 
  curl 'http://localhost:9090/api/v1/query?query=up' > /dev/null 2>&1
done

# Hit Web UI
for i in {1..30}; do 
  curl 'http://localhost:9090/graph' > /dev/null 2>&1
done
```

Wait at least 15 seconds for Prometheus to scrape the new metrics.

Now run the query:
```promql
sum(rate(prometheus_http_requests_total{handler="/metrics"}[5m])) / sum(rate(prometheus_http_requests_total[5m])) * 100
```

This shows what percentage of total HTTP traffic goes to the `/metrics` endpoint (should be around one third) but it could vary!

**Query components:**

**Numerator (top):**
- `prometheus_http_requests_total{handler="/metrics"}` - Selects only requests to /metrics endpoint
- `[5m]` - Look at last 5 minutes of data
- `rate()` - Calculate per-second rate for each time series
- `sum()` - Add up all /metrics requests across all instances/labels

**Denominator (bottom):**
- `prometheus_http_requests_total` - All HTTP requests (no filter)
- `[5m]` - Last 5 minutes
- `rate()` - Per-second rate for each time series
- `sum()` - Total of ALL requests across all handlers/instances

**Final calculation:**
- `/` - Divide /metrics requests by total requests (gives decimal 0.0-1.0)
- `* 100` - Convert to percentage (0-100)

> Note: try the query on the `/graph` endpoint too!

---
---
## (Optional) Going BEYOND! Delete time-series data from Prometheus

 ‼️ WARNING! The following is not recommended for production servers!
 
 Your results can be skewed depending on how many other queries you have been doing, and how many times your Prometheus server has been accessed. To clear your results see [this document](../../z-more-info/promql-docs/delete-time-series-data.md), but use with caution!

---
---
