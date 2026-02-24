# MicroK8s Notes

MicroK8s can be a very simple, efficient, and powerful way to run a Kubernetes cluster. It installs as a snap.

If you want to install MicroK8s, see the following link:
https://microk8s.io/#install-microk8s

If you want to add nodes to the cluster see this link:
https://microk8s.io/docs/clustering

> Note: You will need to *install* microk8s to each node you wish to add. Use the same version of microk8s on each node in the cluster.

I recommend making aliases to Kubernetes commands, for example making an alias from `microk8s` to `kubectl`:

`sudo snap alias microk8s.kubectl kubectl`

Also, you will want to give your user account permissions to MicroK8s so you don't have to constantly type sudo:

`sudo usermod -aG microk8s <user_account>`

> Note: If Kubernetes (or Helm) doesn't recognize your command (or gives TCP 127.0.0.1 errors) then make sure you preface the command with `microk8s`.

---

# MicroK8s Cluster Requirements for Prometheus Course

This document outlines the system requirements for running a 3-node MicroK8s cluster with the Prometheus Community kube-prometheus-stack.

## Cluster Configuration

- **3 Ubuntu Server virtual machines**
- **1 Controller node**
- **2 Worker nodes**
- **Software:** MicroK8s with kube-prometheus-stack (Prometheus, Grafana, Alertmanager, node_exporter, kube-state-metrics)

---

## Minimum Requirements (Tight but Functional)

These are the bare minimum specs that will allow the cluster to run. Expect some performance constraints and slower operations.

### Controller Node
- **CPU:** 2 cores
- **RAM:** 4GB
- **Disk:** 20GB

### Worker Nodes (each)
- **CPU:** 1-2 cores
- **RAM:** 2GB
- **Disk:** 20GB

### Total Cluster Resources
- **CPU:** 4-6 cores
- **RAM:** 8GB
- **Disk:** 60GB

### Expected Performance at Minimum Specs
- Slower pod startup times (2-5 minutes for full stack deployment)
- Possible memory pressure warnings
- Stress tests (`ab`, `openssl speed`) might cause swapping
- Limited headroom for additional workloads

---

## Recommended Requirements (Comfortable Experience)

These specs provide a much better experience for students and are recommended for course labs.

### Controller Node
- **CPU:** 2-4 cores
- **RAM:** 6-8GB
- **Disk:** 30GB

### Worker Nodes (each)
- **CPU:** 2 cores
- **RAM:** 4GB
- **Disk:** 30GB

### Total Cluster Resources
- **CPU:** 6-8 cores
- **RAM:** 14-16GB
- **Disk:** 90GB

### Benefits of Recommended Specs
- Smooth installation and pod deployment
- Room for stress testing without crashes or severe degradation
- Better student experience with responsive dashboards
- Handles the httpd deployment + Apache Benchmark tests comfortably
- Prometheus TSDB has room to grow over time
- More realistic for learning production-like scenarios

---

## Resource Allocation Rationale

### Why the Controller Needs More Resources

The controller node runs:
- Kubernetes control plane components (apiserver, scheduler, controller-manager, etcd)
- Heavy Prometheus stack pods:
  - Prometheus server (~2GB RAM typical usage)
  - Grafana (~512MB RAM)
  - Alertmanager (~256MB RAM)
  - Kube-state-metrics (~128MB RAM)
- Prometheus TSDB storage that grows over time

### Why Workers Can Be Lighter

Worker nodes run:
- Kubelet
- Node-exporter (very lightweight)
- Application workloads (httpd pods are minimal)
- Most Prometheus stack components run on the controller by default

---

## Student Hardware Considerations

Many students will run this cluster on their laptops using VirtualBox, VMware, or similar virtualization platforms.

### Typical Student Laptop
- **16GB total RAM**
- **Allocation:** 14-16GB for VMs + 2GB for host OS
- **Result:** The recommended specs fit within this constraint

### Cloud Alternative
Students can also use cloud providers:
- **AWS:** 3x t3.medium instances (2 vCPU, 4GB RAM each)
- **Azure:** 3x B2s instances (2 vCPU, 4GB RAM each)
- **DigitalOcean:** 3x $24/month droplets (2 vCPU, 4GB RAM each)

---

## Recommendation for Course Materials

**Use the Recommended tier (6-8 CPU cores, 14-16GB RAM total)** in your course documentation.

**Reasons:**
1. Achievable for most students (fits in 16GB laptop)
2. Prevents frustrating "why is everything slow/crashing" scenarios
3. Provides better learning experience
4. Realistic enough to demonstrate production concepts
5. Handles all lab exercises comfortably

**Include the Minimum tier** as a footnote for students with resource constraints, but warn them about potential performance issues.

---

## Disk Space Notes

- **20-30GB per node** is sufficient for the OS, MicroK8s, and Prometheus stack
- Prometheus TSDB grows over time (default 15-day retention)
- If running long-term, consider 40GB+ on the controller
- For short-term labs (days/weeks), 20-30GB is fine

---

## Network Requirements

- All nodes must be on the same network with connectivity to each other
- Recommended: Static IP addresses for stability
- Required ports:
  - Controller: 16443 (API server), 9090 (Prometheus), 3000 (Grafana)
  - Workers: 10250 (kubelet), 9100 (node_exporter)
  - Internal cluster communication: Various ports managed by MicroK8s

---

## Summary Table

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Controller CPU** | 2 cores | 2-4 cores |
| **Controller RAM** | 4GB | 6-8GB |
| **Controller Disk** | 20GB | 30GB |
| **Worker CPU (each)** | 1-2 cores | 2 cores |
| **Worker RAM (each)** | 2GB | 4GB |
| **Worker Disk (each)** | 20GB | 30GB |
| **Total CPU** | 4-6 cores | 6-8 cores |
| **Total RAM** | 8GB | 14-16GB |
| **Total Disk** | 60GB | 90GB |

---

**Bottom Line:** For the best student experience, go with the **Recommended** specifications.