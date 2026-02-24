# ⚙️ Prometheus High Availability Basics (Optional)

This lab introduces the fundamentals of Prometheus High Availability (HA), demonstrating how to run redundant Prometheus instances for reliability and continuous monitoring.

**Prerequisites:**
- 2-3 Linux systems (VMs or cloud instances)
- Prometheus installed on at least 2 systems
- node-exporter running on systems to monitor

**In this lab we will:**
- Understand why Prometheus HA is needed
- Configure multiple Prometheus instances scraping the same targets
- Explore basic HA patterns and their limitations
- Learn about production HA solutions

**Why High Availability Matters:**
- Single Prometheus instance = single point of failure
- Maintenance, crashes, or network issues cause monitoring blind spots
- Critical alerts might be missed during downtime
- Organizations need continuous monitoring for SLAs

> **Important:** This lab demonstrates basic HA concepts. Production HA requires additional components like Thanos, Cortex, or commercial solutions for proper deduplication and long-term storage.

---

## Understanding Prometheus HA Approaches

Prometheus doesn't have built-in clustering or HA. Instead, there are several patterns:

### 1. Active-Active (Identical Instances)

**Pattern:**
- Run 2+ identical Prometheus instances
- Each scrapes the same targets
- Each has its own local storage
- Query either instance for recent data

**Pros:**
- ✅ Simple to set up
- ✅ Automatic failover (query the other instance)
- ✅ No single point of failure

**Cons:**
- ❌ Data duplication (2x storage)
- ❌ No automatic deduplication
- ❌ Queries only see one instance's data
- ❌ Historical data not shared between instances

### 2. Federation

**Pattern:**
- Multiple Prometheus instances scrape different targets
- Central Prometheus federates from all instances
- Hierarchical monitoring structure

**Pros:**
- ✅ Horizontal scaling
- ✅ Geographical distribution
- ✅ Team/service isolation

**Cons:**
- ❌ Central Prometheus is still single point of failure
- ❌ Additional complexity
- ❌ Federation adds latency

### 3. Remote Storage (Production HA)

**Pattern:**
- Multiple Prometheus instances with remote write
- External storage (Thanos, Cortex, Mimir, VictoriaMetrics)
- Deduplication at query time
- Long-term retention

**Pros:**
- ✅ True HA with deduplication
- ✅ Unlimited retention
- ✅ Global query view
- ✅ Horizontal scaling

**Cons:**
- ❌ Complex setup
- ❌ Additional infrastructure
- ❌ Requires external components

**This lab focuses on Pattern #1 (Active-Active) to demonstrate basic concepts.**

---

## Part 1: Setting Up Redundant Prometheus Instances

We'll set up two Prometheus instances that scrape the same targets.

### System Layout

For this lab, we'll use three systems:

- **prometheus1** - First Prometheus instance (10.42.88.10)
- **prometheus2** - Second Prometheus instance (10.42.88.11)
- **target** - System to monitor with node-exporter (10.42.88.12)

> Note: Adjust IP addresses to match your environment. You can use fewer systems by running multiple Prometheus instances on the same host with different ports.

### Install Prometheus on Both Instances

If you haven't already, install Prometheus on both prometheus1 and prometheus2 using the installation script or package manager.

**Verify both are running:**

On prometheus1:
```bash
systemctl status prometheus
curl http://localhost:9090
```

On prometheus2:
```bash
systemctl status prometheus
curl http://localhost:9090
```

### Install node-exporter on Target

On the target system:
```bash
sudo ./node-exporter-install.sh
systemctl status node_exporter
```

---

## Part 2: Configure Identical Scrape Targets

**On prometheus1**, edit the configuration:

```bash
sudo vim /etc/prometheus/prometheus.yml
```

Add a job to scrape the target:

```yaml
  - job_name: 'ha-target'
    static_configs:
      - targets:
        - '<target_ip>:9100'
    scrape_interval: 15s
```

Add an external label to identify this instance:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    replica: 'prometheus1'
    cluster: 'ha-lab'
```

The complete relevant section should look like:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    replica: 'prometheus1'
    cluster: 'ha-lab'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ha-target'
    static_configs:
      - targets:
        - '<target_ip>:9100'
    scrape_interval: 15s
```

Save and restart:

```bash
sudo systemctl restart prometheus
```

**On prometheus2**, edit the configuration:

```bash
sudo vim /etc/prometheus/prometheus.yml
```

Add the **exact same scrape configuration** but with a different replica label:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    replica: 'prometheus2'
    cluster: 'ha-lab'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ha-target'
    static_configs:
      - targets:
        - '<target_ip>:9100'
    scrape_interval: 15s
```

Save and restart:

```bash
sudo systemctl restart prometheus
```

**Why external labels?**
- `replica` identifies which Prometheus instance collected the data
- `cluster` groups related Prometheus instances
- Essential for deduplication in production HA systems
- Helps troubleshooting in multi-instance setups

---

## Part 3: Verify Redundant Scraping

Both Prometheus instances should now be scraping the same target.

### Check Targets on prometheus1

Access: `http://<prometheus1_ip>:9090`

- Go to **Status → Targets**
- You should see:
  - `prometheus` job (localhost)
  - `ha-target` job (your target system)
  - Both should show as "UP"

### Check Targets on prometheus2

Access: `http://<prometheus2_ip>:9090`

- Go to **Status → Targets**
- You should see the **exact same targets**
- Both instances are independently scraping the same endpoints

### Query the Same Metric from Both Instances

**On prometheus1**, run this query:

```promql
up{job="ha-target"}
```

Note the external labels in the result:
```
up{cluster="ha-lab", instance="<target_ip>:9100", job="ha-target", replica="prometheus1"}
```

**On prometheus2**, run the same query:

```promql
up{job="ha-target"}
```

Note the different replica label:
```
up{cluster="ha-lab", instance="<target_ip>:9100", job="ha-target", replica="prometheus2"}
```

**Both instances have the data, but they're independent!**

---

## Part 4: Understanding HA Behavior

### Simulate Failure

Let's simulate prometheus1 failing.

**Stop prometheus1:**

```bash
sudo systemctl stop prometheus
```

**Verify prometheus1 is down:**

Try to access `http://<prometheus1_ip>:9090` - it should fail.

**Query prometheus2:**

Access `http://<prometheus2_ip>:9090` and run:

```promql
up{job="ha-target"}
```

**prometheus2 continues monitoring!** Even though prometheus1 is down, you still have visibility into your infrastructure.

### Restart prometheus1

```bash
sudo systemctl start prometheus
```

Both instances are now running again.

### The Gap Problem

While prometheus1 was stopped, it wasn't collecting metrics. When it restarted:

- ✅ prometheus2 has continuous data
- ❌ prometheus1 has a gap in its data
- ❌ No automatic backfill from prometheus2

**On prometheus1**, query for the last hour:

```promql
up{job="ha-target"}[1h]
```

You'll see a gap during the downtime period.

**On prometheus2**, run the same query - no gap!

**This demonstrates the limitation:** Each instance has its own independent data. There's no automatic synchronization or deduplication.

---

## Part 5: Basic Load Balancing (Optional)

You can use a load balancer to distribute queries across Prometheus instances.

### Simple HAProxy Example

On a separate system (or one of your Prometheus hosts), install HAProxy:

```bash
sudo apt install haproxy -y
```

Edit the configuration:

```bash
sudo vim /etc/haproxy/haproxy.cfg
```

Add to the end:

```
frontend prometheus_frontend
    bind *:9090
    default_backend prometheus_backend

backend prometheus_backend
    balance roundrobin
    option httpchk GET /api/v1/query?query=up
    server prometheus1 <prometheus1_ip>:9090 check
    server prometheus2 <prometheus2_ip>:9090 check
```

Restart HAProxy:

```bash
sudo systemctl restart haproxy
```

**Access the load balancer:**

`http://<haproxy_ip>:9090`

Queries will be distributed across both Prometheus instances. If one is down, HAProxy automatically routes to the healthy instance.

**Limitations:**
- Queries might hit different instances (different data!)
- No session affinity
- Dashboard queries might be inconsistent
- Not recommended for production without proper deduplication

---

## Part 6: Alertmanager HA (Concept)

Alertmanager supports native clustering for HA. This is simpler than Prometheus HA.

### How Alertmanager HA Works

- Multiple Alertmanager instances form a gossip-based cluster
- They communicate via `--cluster.peer` flag
- Alerts are deduplicated across instances
- Only one instance sends each alert notification

### Basic Setup (Conceptual)

**Alertmanager 1:**
```bash
alertmanager \
  --config.file=/etc/alertmanager/alertmanager.yml \
  --cluster.listen-address=0.0.0.0:9094 \
  --cluster.peer=<alertmanager2_ip>:9094
```

**Alertmanager 2:**
```bash
alertmanager \
  --config.file=/etc/alertmanager/alertmanager.yml \
  --cluster.listen-address=0.0.0.0:9094 \
  --cluster.peer=<alertmanager1_ip>:9094
```

**Configure Prometheus to send to both:**

```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - '<alertmanager1_ip>:9093'
          - '<alertmanager2_ip>:9093'
```

**Result:** Even if one Alertmanager instance fails, alerts are still processed and sent.

> Note: This lab focuses on Prometheus HA. For full Alertmanager HA setup, see the official documentation: https://prometheus.io/docs/alerting/latest/high_availability/

---

## Production HA Solutions

For production environments, basic active-active isn't sufficient. You need:

### Thanos

**What it does:**
- Global query view across multiple Prometheus instances
- Automatic deduplication using external labels
- Long-term storage in object storage (S3, GCS, etc.)
- Downsampling for efficient historical queries

**Components:**
- Thanos Sidecar (runs with each Prometheus)
- Thanos Query (global query interface)
- Thanos Store (access object storage)
- Thanos Compactor (downsampling and retention)

**Learn more:** https://thanos.io

### Cortex / Mimir

**What it does:**
- Multi-tenant Prometheus-as-a-Service
- Horizontally scalable
- Long-term storage
- High availability built-in

**Use case:** Large organizations with many teams and clusters

**Learn more:** 
- Cortex: https://cortexmetrics.io
- Mimir: https://grafana.com/oss/mimir/

### VictoriaMetrics

**What it does:**
- Drop-in Prometheus replacement
- Built-in clustering and HA
- Better resource efficiency
- Long-term storage

**Use case:** High-cardinality metrics, resource-constrained environments

**Learn more:** https://victoriametrics.com

### Prometheus Operator (Kubernetes)

**What it does:**
- Manages Prometheus instances in Kubernetes
- Automatic sharding and scaling
- Built-in HA via StatefulSets
- Integration with Thanos

**Use case:** Kubernetes-native monitoring

---

## Best Practices for Prometheus HA

### 1. External Labels

Always configure external labels for:
- `replica` - Identifies the Prometheus instance
- `cluster` - Groups related instances
- `region` - For multi-region deployments

### 2. Consistent Configuration

- Use configuration management (Ansible, Puppet, etc.)
- Keep scrape configs identical across instances
- Sync rule files across replicas
- Version control your configurations

### 3. Monitoring Your Monitoring

Monitor your Prometheus instances themselves:

```promql
# Prometheus instances up
up{job="prometheus"}

# Scrape duration
scrape_duration_seconds{job="prometheus"}

# TSDB head samples
prometheus_tsdb_head_samples

# Rule evaluation failures
prometheus_rule_evaluation_failures_total
```

### 4. Capacity Planning

For active-active HA:
- 2x storage (each instance stores full data)
- 2x CPU/RAM for scraping and queries
- 2x network bandwidth
- Plan for growth

### 5. Retention Alignment

Keep retention policies identical:

```
--storage.tsdb.retention.time=15d
--storage.tsdb.retention.size=50GB
```

Both instances should have the same retention to maintain parity.

---

## Lab Summary

**What you've learned:**

✅ Why Prometheus HA is necessary  
✅ Active-active pattern with redundant instances  
✅ External labels for instance identification  
✅ Behavior during instance failure  
✅ Limitations of basic HA  
✅ Production HA solutions overview  

**Key Takeaways:**

1. **Basic HA = Redundancy, not true HA**
   - Multiple instances provide availability
   - No automatic deduplication or data sharing
   - Each instance operates independently

2. **Production HA requires additional components**
   - Thanos for global view and long-term storage
   - Cortex/Mimir for multi-tenancy
   - VictoriaMetrics for efficiency

3. **Alertmanager HA is simpler**
   - Native clustering support
   - Automatic deduplication
   - Gossip protocol for coordination

4. **Configuration management is critical**
   - Keep configs synchronized
   - Use version control
   - Automate deployment

---

## Troubleshooting

**Instances showing different data:**
- This is normal! Each has independent storage
- Use external labels to identify which instance
- For unified view, implement Thanos or similar

**Target shows as DOWN on one instance but UP on another:**
- Network path might differ between instances
- Check firewall rules
- Verify both instances can reach target
- This is why HA is valuable - one instance still monitors

**High memory/CPU usage with HA:**
- Each instance runs full scrape and storage
- This is expected with active-active
- Plan for 2x resources
- Consider federation or remote storage for scaling

**Gaps in data after instance restart:**
- Normal behavior - no backfill
- This is limitation of basic HA
- Production systems use remote write to avoid this
- Keep instances running to maintain continuity

---

## Extra Credit

**Set up 3+ Prometheus instances:**
- Odd number for quorum-based decisions
- Test failure scenarios
- Practice label-based queries

**Implement basic Alertmanager clustering:**
- Follow the official docs
- Configure gossip protocol
- Test alert deduplication

**Explore Thanos:**
- Set up Thanos sidecar with your Prometheus instances
- Configure S3-compatible storage (MinIO locally)
- Experience global query view
- See automatic deduplication in action

**Try VictoriaMetrics:**
- Single binary alternative to Prometheus
- Built-in clustering
- Compatible with PromQL
- Compare resource usage

**Monitor Prometheus federation:**
- Set up central Prometheus
- Federate from your HA instances
- Create hierarchical monitoring

---

## Additional Resources

**Official Documentation:**
- Prometheus Federation: https://prometheus.io/docs/prometheus/latest/federation/
- Alertmanager HA: https://prometheus.io/docs/alerting/latest/high_availability/

**HA Solutions:**
- Thanos: https://thanos.io/
- Cortex: https://cortexmetrics.io/
- Mimir: https://grafana.com/oss/mimir/
- VictoriaMetrics: https://victoriametrics.com/

**Blog Posts:**
- PromLabs HA Overview: https://promlabs.com/blog/2023/08/31/high-availability-for-prometheus-and-alertmanager-an-overview/
- Robust Perception on HA: https://www.robustperception.io/

---

**Congratulations on learning Prometheus HA fundamentals!** 🎉

Remember: True production HA requires more than redundant instances. Evaluate solutions like Thanos, Cortex, or VictoriaMetrics based on your organization's needs.
