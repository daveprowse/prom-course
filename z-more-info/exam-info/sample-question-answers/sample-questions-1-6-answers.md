# Sample Questions #1-6 - Answers

## Question #1 (Lesson 2: Prometheus Fundamentals)

Which component of the Prometheus ecosystem is responsible for storing time-series data?

**Answer:** C) TSDB (Time Series Database)

**Explanation:** Prometheus uses a custom Time Series Database (TSDB) to store all collected metrics data. The TSDB is optimized for time-series data with efficient compression and fast queries. It stores data locally on disk in the Prometheus server.

**Incorrect Answers:**
- **A) Alertmanager** - Handles alert routing and notifications, does not store metrics data
- **B) Pushgateway** - Temporary storage for metrics from short-lived jobs, not the primary time-series database
- **D) Grafana** - Visualization tool that queries Prometheus but doesn't store the data itself

---

## Question #2 (Lesson 3: Installing Prometheus)

What is the default port that Prometheus uses for its web UI and API?

**Answer:** B) 9090

**Explanation:** Prometheus runs its web UI and HTTP API on port 9090 by default. This is where you access the expression browser, view targets, check configuration, and query metrics via the API endpoint `/api/v1/query`.

**Incorrect Answers:**
- **A) 8080** - Common application port but not Prometheus's default
- **C) 9100** - Default port for node_exporter, not Prometheus itself
- **D) 3000** - Default port for Grafana, not Prometheus

---

## Question #3 (Lesson 4: Observability Concepts - Part 1)

What is the primary difference between Prometheus's pull model and a push model for collecting metrics?

**Answer:** B) Pull model has Prometheus scrape targets via HTTP, push model has targets send metrics to a central collector

**Explanation:** In Prometheus's pull model, the Prometheus server actively scrapes (pulls) metrics from configured targets over HTTP at regular intervals. In a push model (used by systems like StatsD or CloudWatch), the monitored systems actively push their metrics to a central collector. Prometheus's pull model provides better control, service discovery, and prevents targets from overwhelming the monitoring system.

**Incorrect Answers:**
- **A) Pull model requires agents on every monitored system, push model does not** - Both models require something on the monitored system (exporters for pull, agents for push)
- **C) Pull model is only for cloud environments, push model is for on-premise** - Both models work in any environment; this is not the distinguishing factor
- **D) Pull model stores data longer than push model** - Data retention is a configuration choice independent of the collection method

---

## Question #4 (Lesson 4: Observability Concepts - Part 2)

Which service discovery mechanism allows Prometheus to automatically discover targets by reading configuration files that can be updated externally?

**Answer:** C) File-based service discovery

**Explanation:** File-based service discovery (`file_sd_configs`) allows Prometheus to read target information from JSON or YAML files that can be updated by external systems or scripts. Prometheus automatically detects changes to these files and updates its scrape targets accordingly, enabling dynamic target management without restarting Prometheus.

**Incorrect Answers:**
- **A) DNS service discovery** - Discovers targets via DNS A, AAAA, or SRV records, not file-based
- **B) Kubernetes service discovery** - Automatically discovers targets from Kubernetes API, not from files
- **D) Consul service discovery** - Discovers targets from Consul service registry, not from configuration files

---

## Question #5 (Lesson 5: Basic Querying)

In the Prometheus Web UI, you run the query `up`. What does a result of `1` indicate?

**Answer:** B) The target is successfully being scraped by Prometheus

**Explanation:** The `up` metric is automatically created by Prometheus for every scrape target. A value of `1` means the last scrape was successful and the target is reachable. A value of `0` indicates the scrape failed (target is down or unreachable). This is one of the most basic and important health check queries in Prometheus.

**Incorrect Answers:**
- **A) The target has been up for 1 minute** - The value `1` is a boolean indicator, not a duration
- **C) There is 1 instance of the target running** - The value indicates scrape success, not instance count
- **D) The target has 1 metric available** - The value indicates scrape health, not the number of metrics

---

## Question #6 (Lesson 6: Monitoring Fundamentals)

What is the default port that node_exporter uses to expose system metrics?

**Answer:** C) 9100

**Explanation:** node_exporter exposes Linux/Unix system metrics (CPU, memory, disk, network, etc.) on port 9100 by default at the `/metrics` endpoint. This is the standard port that Prometheus scrapes when configured to monitor node_exporter targets.

**Incorrect Answers:**
- **A) 8080** - Common application port but not node_exporter's default
- **B) 9090** - Default port for Prometheus server, not node_exporter
- **D) 9117** - Default port for apache_exporter, not node_exporter
