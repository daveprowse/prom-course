# Sample Questions #7-12

See [this document](../exam-info/sample-question-answers/sample-questions-7-12-answers.md) for the answers.

## Question #7 (Lesson 7: Dashboarding)

When configuring Grafana to visualize Prometheus metrics, what must be specified in the Prometheus data source configuration?

A) The Prometheus server's HTTP API URL (e.g., http://localhost:9090)  
B) The path to Prometheus's configuration file  
C) The Grafana dashboard JSON export location  
D) The Prometheus TSDB data directory path

---

## Question #8 (Lesson 8: Alerting and Rules)

In an alerting rule configuration, what does the `for` parameter specify?

A) How frequently the rule is evaluated  
B) How long the alert condition must be true before the alert fires  
C) How long the alert remains active after firing  
D) Which alertmanager instance receives the alert

---

## Question #9 (Lesson 9: PromQL)

Which PromQL function is used to calculate the 95th percentile from histogram data?

A) `percentile(0.95, metric_name)`  
B) `histogram_quantile(0.95, rate(metric_name_bucket[5m]))`  
C) `quantile(0.95, metric_name)`  
D) `rate(metric_name{percentile="0.95"}[5m])`

---

## Question #10 (Lesson 10: Instrumenting Data)

Which Prometheus metric type should be used to track the current number of active connections to a server (a value that can both increase and decrease)?

A) Gauge  
B) Counter  
C) Histogram  
D) Summary

---

## Question #11 (Lesson 11: Monitoring Linux)

When monitoring Linux systems with node_exporter, what metric would you query to see the total amount of system memory?

A) `node_memory_total`  
B) `node_memory_MemTotal_bytes`  
C) `system_memory_bytes`  
D) `node_mem_total_bytes`

---

## Question #12 (Lesson 12: Monitoring Kubernetes)

When Prometheus runs inside a Kubernetes cluster and uses the kube-prometheus-stack, which component is responsible for exposing Kubernetes object state metrics (like pod count, deployment status)?

A) node-exporter  
B) kubelet  
C) kube-state-metrics  
D) prometheus-operator
