# Timestamp Metrics

Work with time and timestamps in queries. Among other things, this can help to show the time when scrape samples were collected.

**1. Current timestamp:**

```
time()
```

Returns current Unix timestamp.

> Note: For information on converting Unix timestamps to human-readable time, see [this document](../../z-more-info/promql-docs/converting-unix-timestamps.md).

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

**4. Timestamp of sample:**

```
timestamp(up)
```

Shows when each sample was collected.

## From CLI

Check current time:

```bash
curl 'http://localhost:9090/api/v1/query?query=time()' | jq
```

## (Optional) Time-based Filtering

**Note:** Direct time-based filtering (`hour() > 9`) doesn't work in ad-hoc queries. Time filtering is done through:
- Query time ranges (Graph tab's time picker)
- Alerting rules (configured in rules.yml)
- Grafana dashboards (time range selectors)

Here's an example of an alerting rule that *might* use it:

```
- alert: BusinessHoursOnly
  expr: up == 0 and hour() > 9 and hour() < 17
```
