# ⚙️ External K8s Node Monitoring (Optional)

This document demonstrates basic external monitoring of Kubernetes nodes using node-exporter. This is a simpler alternative to the full federation approach shown in Lab 16.

**Use this approach when:**
- You only need basic system metrics (CPU, memory, disk, network)
- You don't need K8s-specific metrics (pods, deployments, etc.)
- You want the simplest possible setup

**Prerequisites:**
- Running MicroK8s cluster (controller + workers)
- External Prometheus server (separate system)
- node-exporter running on all K8s nodes

---

## Verify node-exporter is Accessible

From your external Prometheus server, verify you can reach node-exporter on each K8s node:

**Controller:**
```bash
curl http://<controller_ip>:9100/metrics
```

**Worker1:**
```bash
curl http://<worker1_ip>:9100/metrics
```

**Worker2:**
```bash
curl http://<worker2_ip>:9100/metrics
```

> Note: Replace `<controller_ip>`, `<worker1_ip>`, and `<worker2_ip>` with your actual node IP addresses. If these fail, check firewall rules on the K8s nodes.

Each command should return a long list of metrics.

---

## Add K8s Nodes to Prometheus Configuration

On your external Prometheus server, edit the configuration file:

```bash
sudo vim /etc/prometheus/prometheus.yml
```

Add a new job for the Kubernetes nodes:

```yaml
  - job_name: 'k8s-nodes'
    static_configs:
      - targets:
        - '<controller_ip>:9100'
        - '<worker1_ip>:9100'
        - '<worker2_ip>:9100'
```

> Note: Replace `<controller_ip>`, `<worker1_ip>`, and `<worker2_ip>` with your actual node IP addresses.

Save the file.

---

## Restart Prometheus

```bash
sudo systemctl restart prometheus
```

Verify it's running:

```bash
systemctl status prometheus
```

---

## Verify in Prometheus Web UI

Access your external Prometheus server's web UI:

`http://<prometheus_server_ip>:9090`

**Check targets:**
- Go to **Status → Targets**
- Find the `k8s-nodes` job
- All three targets should show as "UP"

**Run a test query:**

```promql
up{job="k8s-nodes"}
```

You should see all three nodes returning `1`.

**Query node metrics:**

```promql
node_memory_MemAvailable_bytes{job="k8s-nodes"}
```

This shows available memory on each K8s node.

**CPU usage:**

```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle",job="k8s-nodes"}[5m])) * 100)
```

This shows CPU usage percentage for each node.

---

## (Optional) Add to Grafana

If you have Grafana on your external Prometheus server:

1. Go to **Dashboards**
2. Import dashboard **1860** (Node Exporter Full)
3. Select your Prometheus data source
4. Filter by **job = k8s-nodes**

You can now monitor your Kubernetes nodes' system metrics from an external dashboard!

---

## What You're Monitoring

With this setup, you can monitor:

- ✅ CPU usage, load average
- ✅ Memory utilization
- ✅ Disk usage and I/O
- ✅ Network traffic
- ✅ System uptime
- ✅ File descriptor usage

**What you're NOT monitoring:**

- ❌ Pod status and metrics
- ❌ Deployments, services, ConfigMaps
- ❌ Container resource usage
- ❌ K8s API objects
- ❌ Application metrics from within pods

For full Kubernetes monitoring from an external system, use **Lab 16 - Monitoring Kubernetes Externally** which demonstrates Prometheus Federation.

---

## Benefits and Limitations

**Benefits:**
- ✅ Very simple to set up
- ✅ No changes to K8s cluster configuration
- ✅ Monitor basic system health of all nodes
- ✅ Uses existing node-exporter infrastructure
- ✅ Works with any Kubernetes distribution

**Limitations:**
- ❌ Only system-level metrics (not K8s-specific)
- ❌ No pod or container visibility
- ❌ Can't monitor K8s objects (deployments, services, etc.)
- ❌ No application metrics
- ❌ Limited troubleshooting capability

---

## When to Use This vs Lab 16

**Use this approach when:**
- You only care about node health (is it up, CPU/memory usage)
- You're monitoring a simple cluster
- You don't need K8s-specific visibility
- You want the fastest, simplest setup

**Use Lab 16 (Federation) when:**
- You need full K8s visibility (pods, deployments, etc.)
- You want to monitor multiple K8s clusters centrally
- You need container-level metrics
- You're doing production monitoring
- You need kubectl access for cluster management

---

**Done!** You now have basic external monitoring of your Kubernetes nodes.
