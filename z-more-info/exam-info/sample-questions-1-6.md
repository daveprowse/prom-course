# Sample Questions #1-6

See [this document](../exam-info/sample-question-answers/sample-questions-1-6-answers.md) for the answers.

## Question #1 (Lesson 2: Prometheus Fundamentals)

Which component of the Prometheus ecosystem is responsible for storing time-series data?

A) Alertmanager  
B) Pushgateway  
C) TSDB (Time Series Database)  
D) Grafana

---

## Question #2 (Lesson 3: Installing Prometheus)

What is the default port that Prometheus uses for its web UI and API?

A) 8080  
B) 9090  
C) 9100  
D) 3000

---

## Question #3 (Lesson 4: Observability Concepts - Part 1)

What is the primary difference between Prometheus's pull model and a push model for collecting metrics?

A) Pull model requires agents on every monitored system, push model does not  
B) Pull model has Prometheus scrape targets via HTTP, push model has targets send metrics to a central collector  
C) Pull model is only for cloud environments, push model is for on-premise  
D) Pull model stores data longer than push model

---

## Question #4 (Lesson 4: Observability Concepts - Part 2)

Which service discovery mechanism allows Prometheus to automatically discover targets by reading configuration files that can be updated externally?

A) DNS service discovery  
B) Kubernetes service discovery  
C) File-based service discovery  
D) Consul service discovery

---

## Question #5 (Lesson 5: Basic Querying)

In the Prometheus Web UI, you run the query `up`. What does a result of `1` indicate?

A) The target has been up for 1 minute  
B) The target is successfully being scraped by Prometheus  
C) There is 1 instance of the target running  
D) The target has 1 metric available

---

## Question #6 (Lesson 6: Monitoring Fundamentals)

What is the default port that node_exporter uses to expose system metrics?

A) 8080  
B) 9090  
C) 9100  
D) 9117
