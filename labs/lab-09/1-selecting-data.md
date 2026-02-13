# Selecting Data

PromQL selects time series data using metric names and label matchers.

## Basic Selection

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

## From CLI

Query from command line:

```bash
curl 'http://localhost:9090/api/v1/query?query=up'
```

Try a couple of other queries in the place of `up`. Also, pipe to jq (` | jq`) for easier reading!
