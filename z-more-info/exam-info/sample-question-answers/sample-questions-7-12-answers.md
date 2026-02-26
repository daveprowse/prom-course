# Sample Questions #7-12 - Answers

## Question #7 (Lesson 7: Dashboarding)

When configuring Grafana to visualize Prometheus metrics, what must be specified in the Prometheus data source configuration?

**Answer:** A) The Prometheus server's HTTP API URL (e.g., http://localhost:9090)

**Explanation:** To configure Grafana to query Prometheus, you must specify the HTTP URL where Prometheus's API is accessible. Grafana communicates with Prometheus via HTTP requests to endpoints like `/api/v1/query`. The URL is typically `http://localhost:9090` for local setups or `http://<prometheus-ip>:9090` for remote servers. This is configured in Grafana under Connections → Data sources → Add Prometheus data source.

**Incorrect Answers:**
- **B) The path to Prometheus's configuration file** - Grafana doesn't need access to Prometheus's config file; it only queries the running Prometheus server via HTTP
- **C) The Grafana dashboard JSON export location** - Dashboard exports are stored in Grafana, not configured in the data source settings
- **D) The Prometheus TSDB data directory path** - Grafana doesn't directly access Prometheus's storage; it queries via the HTTP API instead

---

## Question #8 (Lesson 8: Alerting and Rules)

In an alerting rule configuration, what does the `for` parameter specify?

**Answer:** B) How long the alert condition must be true before the alert fires

**Explanation:** The `for` parameter defines the duration that an alert expression must continuously evaluate to true before the alert transitions from "pending" to "firing" state. For example, `for: 5m` means the condition must be true for 5 consecutive minutes before firing. This prevents alerts from firing on brief transient issues.

**Incorrect Answers:**
- **A) How frequently the rule is evaluated** - This is controlled by the `evaluation_interval` in the global Prometheus configuration or the `interval` in the rule group
- **C) How long the alert remains active after firing** - Alerts automatically resolve when the condition becomes false; there's no configurable "stay active" duration
- **D) Which alertmanager instance receives the alert** - This is configured in the `alerting` section of prometheus.yml, not in the alerting rule itself

---

## Question #9 (Lesson 9: PromQL)

Which PromQL function is used to calculate the 95th percentile from histogram data?

**Answer:** B) `histogram_quantile(0.95, rate(metric_name_bucket[5m]))`

**Explanation:** The `histogram_quantile()` function calculates quantiles (percentiles) from histogram bucket data. You must use it with the `_bucket` suffix metric and typically wrap the buckets in a `rate()` function. The first argument (0.95) specifies which quantile to calculate - 0.95 represents the 95th percentile, meaning 95% of observations fall below this value.

**Incorrect Answers:**
- **A) `percentile(0.95, metric_name)`** - Not a valid PromQL function; PromQL uses `histogram_quantile` instead
- **C) `quantile(0.95, metric_name)`** - The `quantile()` function exists but calculates quantiles across instant vectors (different labels), not histogram buckets
- **D) `rate(metric_name{percentile="0.95"}[5m])`** - Invalid; percentiles aren't stored as labels in histograms, they're calculated from bucket distributions

---

## Question #10 (Lesson 10: Instrumenting Data)

Which Prometheus metric type should be used to track the current number of active connections to a server (a value that can both increase and decrease)?

**Answer:** A) Gauge

**Explanation:** A Gauge is designed for values that can go up and down, like current connections, temperature, memory usage, or queue size. You can set, increment, or decrement gauge values. This is the appropriate type for any measurement that represents a current state that fluctuates.

**Incorrect Answers:**
- **B) Counter** - Only increases (or resets to zero). Used for cumulative values like total requests, errors, or bytes transferred. Cannot decrease
- **C) Histogram** - Tracks the distribution of values by grouping observations into buckets. Used for request durations or response sizes, not current state
- **D) Summary** - Similar to histogram but calculates quantiles client-side. Also for distributions, not current state values

---

## Question #11 (Lesson 11: Monitoring Linux)

When monitoring Linux systems with node_exporter, what metric would you query to see the total amount of system memory?

**Answer:** B) `node_memory_MemTotal_bytes`

**Explanation:** node_exporter exposes Linux memory information with the prefix `node_memory_` followed by the exact field name from `/proc/meminfo`. The metric `node_memory_MemTotal_bytes` shows the total amount of physical RAM in bytes. This naming convention preserves the original Linux kernel naming from /proc/meminfo.

**Incorrect Answers:**
- **A) `node_memory_total`** - Doesn't follow node_exporter's naming convention; the actual metric name includes `MemTotal_bytes`
- **C) `system_memory_bytes`** - Not a valid node_exporter metric; node_exporter uses the `node_` prefix, not `system_`
- **D) `node_mem_total_bytes`** - Close but incorrect; uses abbreviated `mem` instead of the full `memory` prefix that node_exporter uses

---

## Question #12 (Lesson 12: Monitoring Kubernetes)

When Prometheus runs inside a Kubernetes cluster and uses the kube-prometheus-stack, which component is responsible for exposing Kubernetes object state metrics (like pod count, deployment status)?

**Answer:** C) kube-state-metrics

**Explanation:** kube-state-metrics is a service that listens to the Kubernetes API server and generates metrics about the state of Kubernetes objects (pods, deployments, nodes, services, etc.). It exposes metrics like `kube_pod_status_phase`, `kube_deployment_status_replicas`, and `kube_node_status_condition`. This is distinct from resource metrics like CPU and memory usage.

**Incorrect Answers:**
- **A) node-exporter** - Exports system-level metrics (CPU, memory, disk, network) from the underlying Linux nodes, not Kubernetes object state
- **B) kubelet** - Exposes container resource metrics (CPU/memory usage) and some basic pod metrics, but not comprehensive Kubernetes object state
- **D) prometheus-operator** - Manages Prometheus instances in Kubernetes but doesn't expose metrics itself; it's a controller for creating and managing Prometheus deployments
