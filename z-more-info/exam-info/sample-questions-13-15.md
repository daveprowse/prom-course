# Sample Questions #13-15 (Hands-On)

## Question #13 (PromQL)

You need to create an alert that fires when your service's error rate exceeds 5% over the last 5 minutes. Your application exposes a counter metric `http_requests_total` with a `status` label (values: "success", "error").

Which PromQL expression correctly calculates this error rate?

A) `sum(rate(http_requests_total{status="error"}[5m])) > 0.05`

B) `rate(http_requests_total{status="error"}[5m]) / rate(http_requests_total[5m]) > 0.05`

C) `sum(rate(http_requests_total{status="error"}[5m])) / sum(rate(http_requests_total[5m])) > 0.05`

D) `increase(http_requests_total{status="error"}[5m]) / http_requests_total > 0.05`

See the answer [here](./sample-question-answers/sample-questions-13-answer-and-lab.md).

---

## Question #14 (Prometheus Architecture)

A developer reports that a metric they just added to their application isn't appearing in Prometheus after 2 minutes. The application is running and exposing metrics on `/metrics`. 

What is the FIRST thing you should check to troubleshoot this issue?

A) Check if the Prometheus TSDB has enough disk space

B) Verify the application is listed in the Prometheus scrape configuration and check the target status in the Prometheus UI

C) Restart the Prometheus server to reload the metrics

D) Check if the metric name follows Prometheus naming conventions

See the answer [here](./sample-question-answers/sample-questions-14-answer-and-lab.md).

---

## Question #15 (Instrumentation)

You're instrumenting a payment processing system and need to track the time it takes to process each payment. You want to be able to calculate percentiles (p50, p95, p99) and identify slow transactions.

Which metric type should you use, and what would be the correct Python code?

A) **Counter** - `payment_duration = Counter('payment_duration_seconds', 'Payment duration')`

B) **Gauge** - `payment_duration = Gauge('payment_duration_seconds', 'Payment duration')`

C) **Histogram** - `payment_duration = Histogram('payment_duration_seconds', 'Payment duration')`

D) **Summary** - `payment_duration = Summary('payment_duration_seconds', 'Payment duration')`

See the answer [here](./sample-question-answers/sample-questions-15-answer-and-lab.md).
