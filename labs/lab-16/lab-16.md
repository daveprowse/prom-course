# ⚙️ Lab 16 - Monitoring Kubernetes Externally

**😀 Time for the last lab! I'm not letting you off easy though!**

This lab demonstrates how to monitor your Kubernetes cluster from an external Prometheus server using kubectl access and Prometheus Federation.

**Prerequisites:**
- Running MicroK8s cluster (controller + workers)
- External Prometheus server (separate system)

**In this lab we will:**
- Configure kubectl access to the K8s cluster from an external system
- Set up Prometheus Federation to scrape K8s metrics externally
- Query Kubernetes metrics from the external Prometheus server

**Why this matters:**
- Standard pattern for managing multiple K8s clusters
- Central monitoring survives individual cluster failures
- DevOps/SRE teams manage clusters from workstations
- CI/CD pipelines need API access for deployments

> **Note:** For basic external monitoring of the K8s cluster using only node-exporter (simpler but less powerful), see the separate lab document: [external-k8s-node-monitoring.md](../../z-more-info/additional-labs/external-k8s-node-monitoring.md).

---

## Step 1: Configure MicroK8s API Server

On the **K8s controller**, configure the API server to listen on all network interfaces (not just localhost).

**Edit the API server arguments:**

```bash
sudo vim /var/snap/microk8s/current/args/kube-apiserver
```

Add this line:

```
--bind-address=0.0.0.0
```

Save the file.

**Restart MicroK8s:**

```bash
sudo microk8s stop
sudo microk8s start
```

Wait 30 seconds for all services to come up.

**Verify the API server is listening on all interfaces:**

```bash
sudo ss -tlnp | grep 16443
```

You should see:
```
LISTEN  0.0.0.0:16443
```

If you see `127.0.0.1:16443`, the configuration didn't take effect. Check the file and restart again.

**Note on Verification:** 
- If you run `microk8s kubectl cluster-info` on the controller, it will show `https://127.0.0.1:16443` - this is normal
- MicroK8s uses its internal configuration for local management
- The `ss -tlnp` command confirms the API server is listening on all interfaces
- **The real verification happens in Step 5 when you test from the external system**

> Tip: Keep your `alias kubectl='microk8s kubectl'` on the controller for convenient local management. You don't need to change it.

---

## Step 2: Configure Firewall (If Applicable)

If you have a firewall on the controller, allow port 16443:

**UFW:**
```bash
sudo ufw allow 16443/tcp
```

**firewalld:**
```bash
sudo firewall-cmd --permanent --add-port=16443/tcp
sudo firewall-cmd --reload
```

---

## Step 3: Export and Configure kubeconfig

On the **K8s controller**, export the kubeconfig:

```bash
microk8s config > ~/kubeconfig-external
```

This creates a configuration file for kubectl access.

**View the file:**

```bash
cat ~/kubeconfig-external
```

You'll see it references `https://127.0.0.1:16443` - we need to change this to the controller's public IP.

**Edit the file:**

```bash
sed -i 's/127.0.0.1/<controller_ip>/g' ~/kubeconfig-external
```

> Note: Replace `<controller_ip>` with your controller's actual IP address.

**Verify the change:**

```bash
grep server: ~/kubeconfig-external
```

Should show:
```
    server: https://<controller_ip>:16443
```

---

## Step 4: Copy kubeconfig to External Prometheus Server

From your **external Prometheus server**:

**Create the .kube directory:**

```bash
mkdir -p ~/.kube
```

**Copy the config file:**

```bash
scp <user>@<controller_ip>:~/kubeconfig-external ~/.kube/config
```

> Note: Replace `<user>` with your username and `<controller_ip>` with your controller's actual IP address.

**Verify the file:**

```bash
cat ~/.kube/config | grep server:
```

Should show the controller's public IP, not 127.0.0.1.

---

## Step 5: Install kubectl on External System

**For Ubuntu/Debian:**

```bash
sudo snap install kubectl --classic
```

**Verify installation:**

```bash
kubectl version --client
```

---

## Step 6: Test kubectl Access

**Get cluster info:**

```bash
kubectl cluster-info
```

Expected output:
```
Kubernetes control plane is running at https://<controller_ip>:16443
CoreDNS is running at https://<controller_ip>:16443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

> Note: It should show your controller's public IP, NOT 127.0.0.1

**Get nodes:**

```bash
kubectl get nodes
```

Expected output:
```
NAME         STATUS   ROLES    AGE   VERSION
controller   Ready    <none>   18d   v1.34.3
worker1      Ready    <none>   18d   v1.34.3
worker2      Ready    <none>   18d   v1.34.3
```

**Get pods across all namespaces:**

```bash
kubectl get pods -A
```

You should see all pods from your cluster!

**Excellent!** You now have remote kubectl access to your Kubernetes cluster.

---

## Step 7: Configure Prometheus Federation

Now let's configure your external Prometheus to scrape metrics from the in-cluster Prometheus using **federation**. This is how organizations monitor multiple Kubernetes clusters from a central Prometheus server.

**What is Federation?**
- The in-cluster Prometheus collects all K8s metrics
- The external Prometheus pulls selected metrics from the in-cluster Prometheus via `/federate` endpoint
- You get centralized monitoring without running everything in one place

### Expose the In-Cluster Prometheus

On the **K8s controller**, check the current Prometheus service type:

```bash
kubectl get svc -n prometheus stable-kube-prometheus-sta-prometheus
```

If it shows `ClusterIP` or `LoadBalancer` type, ensure it's accessible via NodePort:

```bash
kubectl patch svc stable-kube-prometheus-sta-prometheus -n prometheus -p '{"spec": {"type": "NodePort"}}'
```

> Note: If you completed Lab 15, then the Kubernetes cluster should have a ClusterIP address set up.

**Find the NodePort:**

```bash
kubectl get svc -n prometheus stable-kube-prometheus-sta-prometheus
```

Look for the port mapping. It will show something like `9090:31894/TCP`. The second number (31894 in this example) is the NodePort you'll use.

**Make note of this NodePort number.**

### Test Federation Endpoint

From your **external Prometheus server**, test that you can reach the federation endpoint:

```bash
curl http://<controller_ip>:<nodeport>/api/v1/query?query=up
```

Replace `<controller_ip>` with your controller IP and `<nodeport>` with the NodePort from above.

This should return a large JSON response showing all the `up` metrics from the K8s cluster. The output will be very long - that's expected and shows the endpoint is working!

> **Tip:** To make the output more readable, pipe it through `jq`:
> ```bash
> curl http://<controller_ip>:<nodeport>/api/v1/query?query=up | jq
> ```

### Configure Federation on External Prometheus

On your **external Prometheus server**, edit the configuration:

```bash
sudo vim /etc/prometheus/prometheus.yml
```

Add a new federation job at the end of the `scrape_configs` section:

```yaml
  - job_name: 'k8s-cluster-federation'
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job="prometheus"}'
        - '{job="kube-state-metrics"}'
        - '{job="node-exporter"}'
        - '{__name__=~"kube_.*"}'
        - '{__name__=~"container_.*"}'
    static_configs:
      - targets:
        - '<controller_ip>:<nodeport>'
```

Replace `<controller_ip>` and `<nodeport>` with your actual values.

**What this configuration does:**
- `honor_labels: true` - Preserves original labels from the K8s cluster
- `metrics_path: '/federate'` - Uses the federation endpoint instead of `/metrics`
- `match[]` - Selects which metric families to pull:
  - Prometheus internal metrics
  - kube-state-metrics (K8s object states)
  - node-exporter metrics
  - All metrics starting with `kube_`
  - All metrics starting with `container_`

Save the file.

**Restart external Prometheus:**

```bash
sudo systemctl restart prometheus
```

**Verify Prometheus restarted successfully:**

```bash
systemctl status prometheus
```

---

## Step 8: Verify Federation is Working

Access your **external Prometheus** web UI:

`http://<prometheus_server_ip>:9090`

### Check the Federation Target

- Go to **Status → Targets**
- Find the `k8s-cluster-federation` job
- It should show as **"UP"** with the controller IP and NodePort

If it shows as "DOWN", check:
- NodePort is correct
- Controller firewall allows the NodePort
- Prometheus configuration has no YAML syntax errors

### Query Federated Kubernetes Metrics

Try these queries in your external Prometheus to verify you're receiving K8s metrics:

**Pod information:**
```promql
kube_pod_info
```

This should show all pods running in your K8s cluster.

**Node status:**
```promql
kube_node_status_condition
```

This shows the health status of each node.

**Container memory usage in the prometheus namespace:**
```promql
container_memory_usage_bytes{namespace="prometheus"}
```

This shows memory usage of containers in the prometheus namespace.

**Deployment replica status:**
```promql
kube_deployment_status_replicas
```

This shows the desired vs actual replicas for all deployments.

**Count pods per namespace:**
```promql
count by (namespace) (kube_pod_info)
```

This aggregates pod counts by namespace.

**You can go on and on. There are plenty of metrics to scrape! See the [Extra Credit](#extra-credit) section for more!**

## 🏁 That was the last LAB! YEAH! 🏁


---

## Troubleshooting

**kubectl shows "The connection to the server was refused":**
- Check API server is listening: `sudo ss -tlnp | grep 16443` on controller
- Verify firewall allows port 16443
- Confirm IP address in `~/.kube/config` is correct

**kubectl shows "Unable to connect to the server: x509: certificate signed by unknown authority":**
- The kubeconfig includes the CA certificate - this shouldn't happen
- Verify you copied the complete config file
- Try: `kubectl --insecure-skip-tls-verify get nodes` (not recommended for production)

**kubectl works on controller but not externally:**
- Check if controller IP is correct in external `~/.kube/config`
- Verify network connectivity: `telnet <controller_ip> 16443` from external system
- Check firewall on controller

**kubectl cluster-info shows 127.0.0.1 on external system:**
- Verify you edited the config file correctly: `grep server: ~/.kube/config`
- Re-run: `sed -i 's/127.0.0.1/<controller_ip>/g' ~/.kube/config` (replace with actual IP)

**Federation target shows as DOWN:**
- Verify NodePort: `kubectl get svc -n prometheus stable-kube-prometheus-sta-prometheus`
- Test endpoint manually: `curl http://<controller_ip>:<nodeport>/api/v1/query?query=up`
- Check Prometheus logs: `sudo journalctl -u prometheus -f`
- Verify YAML indentation in prometheus.yml

**Federation queries return no data:**
- Check that the target is UP in Status → Targets
- Wait 30-60 seconds after restarting Prometheus for first scrape
- Verify the match[] parameters in federation config
- Try a simpler query first: `up{job="k8s-cluster-federation"}`

---

## Lab Complete!

**You now have:**

✅ **Remote kubectl access** to manage your K8s cluster from an external system

✅ **Prometheus Federation** pulling K8s metrics to a central monitoring server

✅ **Centralized monitoring** that survives individual cluster failures

✅ **Production-ready patterns** for multi-cluster environments

**What you've learned:**
- How to expose K8s API server for external access
- How to configure kubectl for remote cluster management
- How Prometheus Federation works
- How to centralize monitoring across multiple K8s clusters

**Real-world applications:**
- Managing dev/staging/prod clusters from one workstation
- Central monitoring dashboard for multiple K8s environments
- CI/CD pipelines deploying to K8s clusters
- SRE teams monitoring distributed infrastructure

**Security Note:** In production, you would:
- Use service accounts with RBAC instead of admin credentials
- Implement VPN or bastion host access
- Enable proper TLS verification
- Use network policies to restrict API access
- Implement authentication and authorization controls

---

## Extra Credit

**Add Grafana to External Prometheus:**

Install Grafana on your external Prometheus server and import K8s dashboards:
- **15757** - Kubernetes Cluster Monitoring
- **12740** - Kubernetes Monitoring
- **11074** - Node Exporter for Prometheus Dashboard

**Monitor Multiple Clusters:**

Repeat the federation setup for additional K8s clusters. Add multiple targets to the federation job:

```yaml
  - job_name: 'k8s-cluster-federation'
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job="prometheus"}'
        - '{__name__=~"kube_.*"}'
    static_configs:
      - targets:
        - '<cluster1_ip>:<nodeport>'
        - '<cluster2_ip>:<nodeport>'
        - '<cluster3_ip>:<nodeport>'
```

**Automate kubectl Config Updates:**

Create a script to automatically fetch and configure kubectl access:

```bash
#!/bin/bash
scp <user>@<controller_ip>:~/kubeconfig-external ~/.kube/config
sed -i 's/127.0.0.1/<controller_ip>/g' ~/.kube/config
kubectl get nodes
```

> Note: Replace `<user>` and `<controller_ip>` with your actual username and controller IP address.

**Configure kubectl Contexts:**

Manage multiple clusters with kubectl contexts:

```bash
# Add a context for this cluster
kubectl config set-context microk8s-prod --cluster=microk8s-cluster --user=admin

# Switch between clusters
kubectl config use-context microk8s-prod

# View all contexts
kubectl config get-contexts
```

---
## Extra EXTRA Credit

What if your main Prometheus server goes down?

Consider Prometheus high availability (HA) and redundancy. 

Check out this [optional lab](../../z-more-info/additional-labs/prometheus-ha-basics.md) for details!

