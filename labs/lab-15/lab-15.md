# ⚙️ Lab 15 - Prometheus and Grafana in Kubernetes

In this lab we will:

- Install Prometheus and Grafana to a Kubernetes cluster using Helm.
- Connect to Prometheus and Start Monitoring.
- Connect to Grafana Dashboards and monitor with alerts.

> Note: This is the most complex and massive lab so far. Take it step-by-step!

> Note: If you do not have a Kubernetes cluster or minikube running, see the following in the *z-more-info* directory:
> - [MicroK8s Setup](../../z-more-info/microk8s/microk8s-notes.md)
> - [Vanilla Kubernetes Setup](../../z-more-info/k8s-scripts/README.md)
> - [Minikube](../../z-more-info/minikube/minikube-install.md)
>
> **Important!** I recommend using microk8s for this video course because it combines easy-of-use with great functionality. That's what I will be using in the lab.

---

## Part 1: Installing the Prometheus Stack

The Prometheus Community maintains a group of Helm charts that can install Prometheus, node_exporter, alertmanager, kube metrics, and Grafana all at once. Instead of re-inventing the wheel, let's make use of what already exists!

Before beginning the lab, be sure that your controller and workers are up and running properly:

`kubectl get nodes`

> Note: If you are using minikube then run `minikube start`.

### Install Helm and Repositories

First let's install Helm on the Kubernetes controller. Here's the one-liner to install Helm v3.

`curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash`

> Note: That should work on most Linux distributions. See [this link](https://helm.sh/docs/intro/install/) for more Helm installation options.

Check if it installed properly and is executable as a binary:

`helm version`

Now, add the stable Helm charts:

`helm repo add stable https://charts.helm.sh/stable`

Next, add the Prometheus Community Helm repo:

`helm repo add prometheus-community https://prometheus-community.github.io/helm-charts`

Finally, view the available repos within the prometheus-community:

`helm search repo prometheus-community`

There will be a bunch! From here, you can see many awesome (and commonly used) exporters and their versions.

Done!

### Set up and Install Prometheus and Tools

Now we'll setup and install Prometheus, node_exporter, alertmanager, and grafana - which are all part of the "kube-prometheus-stack".

Create a Prometheus namespace:

`kubectl create namespace prometheus`

Build a custom values file for the namespace:

> Note: Without this custom configuration, Grafana pods may fail to start due to port conflicts between the dashboard and datasource sidecar containers. Both sidecars try to use the same health server port by default, so we assign different ports to each.

Create a file called `prometheus-values.yaml` in your home directory with the following content:

```yaml
grafana:
  sidecar:
    dashboards:
      enabled: true
      env:
        SKIP_TLS_VERIFY: "true"
        IGNORE_ALREADY_PROCESSED_CONFIG_MAPS: "true"
        ENABLE_5XX: "false"
        HEALTH_SERVER_PORT: "8081"
    datasources:
      enabled: true  
      env:
        SKIP_TLS_VERIFY: "true"
        ENABLE_5XX: "false"
        HEALTH_SERVER_PORT: "8082"
```

Save the file.

Install the Prometheus stack using Helm and referring to our values file:

`helm install stable prometheus-community/kube-prometheus-stack -n prometheus -f prometheus-values.yaml`

**Give this a minute to complete. (It will be silent.)**


> Note (alternative): You might be able to get away with omitting the values file and install with the following command, but this method could cause the Grafana pods (and subsequently, the Grafana server) to fail. 

>```
>helm install stable prometheus-community/kube-prometheus-stack -n prometheus
>```


> Note: If using MicroK8s, precede the last command with `microk8s` (even if you have an alias). Perform this process with other K8s distributions such as minikube if necessary.

---
> OPTIONAL: If you want to run the command in a more verbose fashion here are some options:

```
# Option 1: Debug mode (very verbose)
helm install stable prometheus-community/kube-prometheus-stack -n prometheus -f prometheus-values.yaml --debug

# Option 2: Wait and show progress (recommended)
helm install stable prometheus-community/kube-prometheus-stack -n prometheus -f prometheus-values.yaml --wait --timeout 10m

# Option 3: Both!
helm install stable prometheus-community/kube-prometheus-stack -n prometheus -f prometheus-values.yaml --debug --wait --timeout 10m

Or watch the install in realtime (with TMUX):
# Terminal 1: Run helm install
helm install stable prometheus-community/kube-prometheus-stack -n prometheus -f prometheus-values.yaml

# Terminal 2: Watch pods being created
watch kubectl get pods -n prometheus

or

watch microk8s kubectl get pods -n prometheus
```
---

### Verify Pods and Services

When done, issue the following command:

`kubectl get pods -n prometheus`

> Note: For minikube, use the following command to see the pods:
> `minikube kubectl -- get pods --namespace prometheus`

Take a look at the pods that have been created by the Helm chart. You should see pods for:

- Prometheus itself
- Node exporters (for the controller and each worker in the cluster)
- Grafana
- Alertmanager
- Metrics

Verify that they are all running. There should be about a dozen in total. Run the command again until you see that all pods' status are "Running".

> Note: It may take a couple minutes for all pods to run. This is especially true for minikube and micro instances on the cloud. The more resources you can spare the better!

As you can see, a *lot* of the K8s work has been taken care of for you. Enjoy!

Now check out the services associated with the stack and the IP addresses they are using:

`kubectl get svc -n prometheus`

You should see something similar to:

```console
user@kvm-k8s-controller:$ kubectl get svc -n prometheus
NAME                                      TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)                         AGE
alertmanager-operated                     ClusterIP      None             <none>        9093/TCP,9094/TCP,9094/UDP      43m
prometheus-operated                       ClusterIP      None             <none>        9090/TCP                        43m
stable-grafana                            ClusterIP      10.107.83.115    <none>        80:31129/TCP                    43m
stable-kube-prometheus-sta-alertmanager   ClusterIP      10.106.188.78    <none>        9093/TCP,8080/TCP               43m
stable-kube-prometheus-sta-operator       ClusterIP      10.99.158.76     <none>        443/TCP                         43m
stable-kube-prometheus-sta-prometheus     ClusterIP      10.105.51.243    <none>        9090:32696/TCP,8080:32616/TCP   43m
stable-kube-state-metrics                 ClusterIP      10.102.136.212   <none>        8080/TCP                        43m
stable-prometheus-node-exporter           ClusterIP      10.107.8.244     <none>        9100/TCP                        43m
```

> Note: Your IP addresses will differ.

> Note: to see the IPs in minikube use the following command:
> 
> `minikube kubectl -- get svc -n prometheus`

You should be able to connect to Prometheus locally via it's ClusterIP address. (Use the "stable-kube-prometheus-sta-prometheus" pod's IP.)

For example:

`curl http://10.105.51.243:9090`

> Note: Want to see *all* information about the namespace and associated datasets? Try `kubectl get all -n prometheus`

## Part 2: Remote Access to the Cluster

If you installed to a microk8s/vanilla K8s cluster or minikube then you will probably have to assign an IP to access the services (or expose the services).

> Note: If you have installed this stack to a cloud-based cluster (AWS, Azure, GKE, Grafana-Cloud) then there is probably an EXTERNAL-IP address assigned to Prometheus and to Grafana. You can access Prometheus (port 9090) and Grafana (port 80) using the displayed IP addresses.

#### Vanilla K8s/microK8s

You have two options to add an external IP to your Prometheus and Grafana services: the service editing option and the one-line command option.

*Service editing*

- `kubectl edit svc stable-kube-prometheus-sta-prometheus -n prometheus`
  - Find `type: ClusterIP` and change it to: `type: LoadBalancer`
  - Add the syntax shown below.
- `kubectl edit svc stable-grafana -n prometheus`
  - Again, find `type: ClusterIP` and change it to: `type: LoadBalancer`
  - Again, add the syntax shown below.

> **Note:** If you are working on a cloud-based system, simply configuring the "ClusterIP" option is often enough. If not, follow the next step.

- Set the IP address within the service configuration files with a new line directly under spec >  clusterIPs:
    
    ```console
    externalIPs:
    - <ip address>
    ```

*One-line command*

- Issue the following two commands to set the External-IP address as a LoadBalancer configuration:
  - `kubectl patch svc stable-kube-prometheus-sta-prometheus -n prometheus -p '{"spec": {"type": "LoadBalancer", "externalIPs":["<ip_address>"]}}'`
  - `kubectl patch svc stable-grafana -n prometheus -p '{"spec": {"type": "LoadBalancer", "externalIPs":["<ip_address>"]}}'`
   > Note: Remember to replace `<ip_address>` with the IP address of your Kubernetes controller!

Check your work with `kubectl get svc -n prometheus`. You should see the EXTERNAL-IP addresses and they should now be accessible from remote systems.

#### minikube

For minikube, you'll need to patch the IP addresses for the Prometheus and Grafana services and then expose those services so you can connect to them via the web browser.

1. Patch the IPs for Prometheus and Grafana:

    `minikube kubectl -- patch svc stable-kube-prometheus-sta-prometheus -n prometheus -p '{"spec": {"type": "LoadBalancer", "externalIPs":["<IP_address>"]}}'`

    `minikube kubectl -- patch svc stable-grafana -n prometheus -p '{"spec": {"type": "LoadBalancer", "externalIPs":["<IP_address>"]}}'`

    > Note: Use the actual IP address of the system that is hosting the minikube. So remove `<IP_address>` and replace it with the actual IP address.

    > Note: You could also do service editing as shown in the "Vanilla K8s" section previously.

2. Expose the Prometheus and Grafana services. Run each of the following commands in separate terminals.

    `minikube service stable-kube-prometheus-sta-prometheus --namespace=prometheus`

    `minikube service stable-grafana --namespace=prometheus`

    > Note: Each one should attempt to open a web browser automatically. If not, attempt to connect manually to the link named in the URL field that is displayed.

## Part 3: Monitoring the Cluster with Prometheus

Now, connect to the Prometheus web UI

`http:<ip_address>:9090`

> Note: For minikube, use the address and port that was exposed and connect locally.

In the expression field type the following query:

`kube_configmap_info`

View the content in Table mode.

You should see a whole boatload of metrics that come from the *kube-state-metrics* container (note the IP of that container). These metrics (and others) are all built into the Prometheus stack that we installed. (Yet another reason to use this Helm chart.)

Now issue the following query:

`kube_pod_ips`

Review the IP addresses used by the controller and workers, and the containers.

View the "Alerts" section. Bask in the glory of pre-built alerts!

### Using Promtool for Analysis

Promtool provides powerful commands for analyzing your Prometheus time-series database (TSDB).

First, get the exact Prometheus pod name:
```bash
kubectl get pods -n prometheus | grep prometheus
```

You should see a pod named `prometheus-stable-kube-prometheus-sta-prometheus-0`. Access it:
```bash
kubectl exec -it -n prometheus prometheus-stable-kube-prometheus-sta-prometheus-0 -- sh
```

You should be placed in the `/prometheus` directory by default.

**Check the Health of the TSDB**

Run the command:

```bash
promtool check healthy
```

You should see SUCCESS. We've used this tool before on our solo Prometheus server. It works the same way here.

**Check the TSDB structure:**
```bash
ls -la /prometheus
```

You should see:
- `chunks_head/` - In-memory chunk storage
- `wal/` - Write-Ahead Log directory
- Possibly block directories (named like `01HXXXXXXXXXXXXX`) if Prometheus has been running 2+ hours

**View WAL segments:**
```bash
ls -lh /prometheus/wal/
```

This shows the WAL segment files (e.g., `00000000`, `00000001`) where Prometheus stores incoming data before creating blocks.

**Dump TSDB samples:**
```bash
promtool tsdb dump /prometheus | head -50
```

This dumps actual sample data from the database, showing the raw metrics being stored. You'll see metrics in the format:
```
{__name__="metric_name", label1="value1", label2="value2"} 0 1771422157855
```

**Analyze TSDB (if blocks exist):**
```bash
promtool tsdb analyze /prometheus
```

> Note: If you see "no blocks found", your Prometheus installation is fresh (less than 2 hours old). Prometheus creates TSDB blocks every 2 hours. Your data is currently in the WAL. You can either wait 2+ hours and try again, or skip to the benchmark command below.

When blocks exist, this command shows:
- Number of series
- Label cardinality
- Memory usage by metric
- Block duration and samples

Exit the pod when done:
```bash
exit
```

> Note: These commands help diagnose performance issues, understand cardinality, and optimize your Prometheus deployment.

### Monitoring Node Resources with PromQL

Let's explore some useful queries for monitoring your Kubernetes nodes, then we'll optimize them using recording rules.

**CPU Idle Percentage per Node:**
```
avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))
```

This shows the average idle CPU percentage for each node over the last 5 minutes. Values closer to 1 (100%) mean the node is mostly idle.

**CPU Usage Percentage per Node:**
```
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

This inverts the idle percentage to show actual CPU usage. Higher values indicate busier nodes.

**Memory Utilization Ratio per Node:**
```
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes
```

This calculates the memory utilization as a ratio (0-1). Values closer to 1 indicate high memory usage.

These queries are useful for quick health checks, identifying nodes under load, and deciding when to scale your cluster.

### Creating Recording Rules

The CPU and memory queries above are useful but computationally expensive - Prometheus has to calculate them every time you run them. **Recording rules** pre-compute these queries and save the results as new time series, making dashboards faster and reducing load on Prometheus.

Let's create recording rules for the CPU usage and memory utilization queries.

**1. Create a PrometheusRule:**

In Kubernetes with the Prometheus Operator, rules are created using `PrometheusRule` custom resources.

Create a file called `rule1.yaml`:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: node-recording-rules
  namespace: prometheus
  labels:
    release: stable
spec:
  groups:
  - name: node_recording_rules
    interval: 30s
    rules:
    - record: instance:node_cpu:avg_rate5m
      expr: |
        100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
    - record: instance:node_memory_utilization:ratio
      expr: |
        (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes
```

Note: These are the same expressions we tested manually above, now saved as recording rules.

**2. Apply the rule:**
```bash
kubectl apply -f rule1.yaml
```

**3. Verify the rule was created:**
```bash
kubectl get prometheusrule -n prometheus
```

You should see `node-recording-rules` in the list.

**4. Check that Prometheus loaded the rules:**

In the Prometheus UI, go to **Status → Rules**. You should see a rule group called `node_recording_rules` with two rules:
- `instance:node_cpu:avg_rate5m`
- `instance:node_memory_utilization:ratio`

The rules evaluate every 30 seconds. Wait up to 1-2 minutes for the first evaluation to complete.

**5. Query the recorded metrics:**

In the Prometheus UI, run these queries:
```
instance:node_cpu:avg_rate5m
```

This shows CPU usage percentage for each node (same result as the manual query, but pre-computed).
```
instance:node_memory_utilization:ratio
```

This shows memory utilization ratio for each node.

**Benefits of recording rules:**
- Faster dashboard queries (pre-computed results)
- Reduced load on Prometheus
- Simplified complex expressions
- Historical data for expensive calculations

You can now use these simple metric names (`instance:node_cpu:avg_rate5m`) in dashboards instead of the complex PromQL expressions.

> Note: If you would like to remove the rule from your cluster, use the `kubectl delete -f rule1.yaml` command.
>
> Note: If you would like to check the logs for a particular pod, run a command similar to: 
> 
> `kubectl logs -n prometheus prometheus-stable-kube-prometheus-sta-prometheus-0 -c prometheus
`

---

#### Sidebar

If you liked working within the pod during this sub-lesson, and want to do more testing from within the pod, check out [this document](../../z-more-info/microk8s/testing-kubernetes-prometheus-pod.md). It includes testing commands that you should be able to run from within the pod. For learning only. In the field, avoid exec'ing into pods unless absolutely necessary!

---
  
## Part 4: Monitoring the Cluster with Grafana

Now, let's connect to the Grafana server from the browser. Remember that we are simply connecting via port 80. In the field you will want to incorporate TLS on the front-end so that you have an extra layer of security for your Grafana server.

`http://<ip_address>`
  
The username is `admin` but the password needs to be deciphered and decoded with the following command at your Kubernetes controller or minikube system:

`kubectl get secret --namespace prometheus stable-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo`

Copy and paste the passcode to your Grafana login screen and login. You should see the "Welcome to Grafana" home page.

### Examine Dashboards

Let's take a look at a few of the built-in dashboards. Take a minute to examine each of these:

- Kubernetes / Compute Resources/ Node (pods)
  - Check the different nodes (or all at once!)
- Kubernetes / Compute Resources/ Workload
  - Select the *prometheus* namespace and examine the different workloads.  
- Node Exporter/ Nodes
  - Stress out your workers!
    - Try `openssl speed -multi $(nproc --all)` to stress the CPUs on the worker nodes.
    - Or the `stress` program: `stress -c 1 -m 10`
  - View the results in the dashboard! (Be ready for delays in data - as much as 5 minutes depending on the setup and systems.)
  - *Leave these tests running for later analysis.*
  - *Bonus*: Check out the stress that is being imposed on the server housing your Kubernetes cluster. Use `top` or a similar program. At this point it should be working harder!

---
*♥️  Shout out to the Prometheus Monitoring Community! ♥️*

https://github.com/prometheus-community

---

### Examine Kubelet Metrics

On your Kubernetes controller run the following command:

`kubectl get nodes -o wide`

This should show the controller IP address (or minikube IP address if you are using minikube).

Now, attempt to query the main Prometheus metrics for that IP address:

`curl http://<ip_address>/metrics`

This should show the metrics for Prometheus that are being scraped.

Now, find out the IP address of the container that is providing kubelet metrics:

`kubectl --namespace prometheus get pods -l "release=stable" -o wide`

> Note: This is a formal way of issuing the command. Lots of abbreviations and truncations you can do!

You should see all pods that are running including one called *stable-kube-state-metrics*. Look at the IP address that this is being served on. Then, curl that Ip address on port 8080 (the default for this Prometheus stack). Example:

`curl http://192.168.86.161:8080/metrics | less`

That's a lot of metrics. Effectively, these are what Prometheus is scraping from and displaying when you run PromQL queries in the web UI. They are also what are displayed in the Grafana dashboards.

**Again, it is the legend.**

### Examine Kubelet Metrics in Grafana

Open the following dashboard:

Kubernetes / Kubelet

Spend a minute looking at the gauges and counters in the dashboard.

This is a pretty good representation of the important metrics that Prometheus is scraping from your kubelet. You should see:

- Running Kubelets
- Running Pods
- Running Containers
- Operations per second (known as ops/s) which will count total ops, error rate, and more
- Storage operation information
- PLEG gauges (PLEG = Pod Lifecycle Event Generator). Example, PLEG relist rate should hover around 1 relist per second.

***This is a great first stop to see the health of your kubelet.***

### Creating a Custom Dashboard with Recording Rules

Now let's create a simple custom dashboard using the recording rules we created earlier.

**1. Create a new dashboard:**

In Grafana, click **Dashboards** → **New** → **New Dashboard**

**2. Add a panel for CPU usage:**

- Click **Add visualization**
- Select **prometheus** as the data source
- In the query field, enter:
```
  instance:node_cpu:avg_rate5m
```
- In the panel title field (top right), enter: **Node CPU Usage %**
- Change visualization type to **Stat** (shows current values)
- Save the Dashboard (as **Node Resource Monitoring**). Click **Apply** if necessary.

**3. Add a panel for memory utilization:**

Show the dashboard in it's monitoring mode. You might have to click "Back to Dashboard", or save it or something similar. At that point you should be able to add another panel. 

- Click **Add** → **Visualization**
- Select **prometheus** as the data source
- In the query field, enter:
```
  instance:node_memory_utilization:ratio * 100
```
- Title: **Node Memory Utilization %**
- Visualization: **Gauge**
- Under "Gauge" → "Max" → enter **100**
- Save the Dashboard or click **Apply**
- Click "Back to Dashboard" to see both panels running at the same time.

**4. Compare with the manual query:**

- Add another panel
- Query: 
```
  (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
```
- Change the visualization to Gauge.
- Title: **Node Memory Utilization % (Calculated)**

> Note: If this query shows "No data", wait a few seconds and refresh. Both this calculated query and the recording rule should show identical results.

- Save the dashboard

Notice how both memory usage panels show the same data, but the recording rule query is simpler and loads faster.

**Benefits you just demonstrated:**
- Recording rules simplify dashboard queries
- Pre-computed metrics load instantly
- Complex PromQL expressions become reusable metric names


---

## Part 5: Deploying & Monitoring a Web Server

Now, let's deploy a basic HTTP web server to the Kubernetes cluster and monitor it from Grafana. We'll also demonstrate proper label strategy.

### Understanding Label Strategy

Labels are key-value pairs attached to Kubernetes objects and metrics. A good label strategy helps you:
- Filter and aggregate metrics effectively
- Organize workloads by environment, team, or application
- Create meaningful alerts and dashboards

**Common label patterns:**
- `environment`: prod, staging, dev
- `team`: platform, frontend, backend
- `app`: webserver, database, cache
- `version`: v1.0, v2.0

### Deploy the Web Server with Labels

> Note: This lab may require additional configurations for minikube users.

- First, create a new namespace on your K8s controller (or minikube):
  - `kubectl create ns http`
- View it and verify that it was created:
  - `kubectl get ns`
- Copy the `http.yml` file to your controller and create a pod based on that config:
  - `kubectl apply -f http.yml`
- Verify that all pods are running before continuing:
  - `kubectl get all -n http`

> Note: this may take a minute to complete because it has to fetch and install the web server.

When done, it should look similar to this:

```console
sysadmin@controller:~$ kubectl get all -n http
NAME                                    READY   STATUS    RESTARTS   AGE
pod/httpd-deployment-67fcb6ffc9-lmh6r   1/1     Running   0          48s
pod/httpd-deployment-67fcb6ffc9-p6xgv   1/1     Running   0          48s

NAME                    TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
service/httpd-service   NodePort   10.110.132.145   <none>        8080:32321/TCP   48s

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/httpd-deployment   2/2     2            2           48s

NAME                                          DESIRED   CURRENT   READY   AGE
replicaset.apps/httpd-deployment-67fcb6ffc9   2         2         2       48s
```

Make note of the ports being used by *service/httpd-service* - specifically the second port (in this case port 32321). Try connecting to the web server on that port using the controller node's main IP address. For example:

`curl http://10.42.88.100:32321`

If the return message says that "It works!" then you are good.

### Querying with Labels

Now let's see how labels help you filter and aggregate metrics.

**Check the labels on your deployment:**

```bash
kubectl get pods -n http --show-labels
```

You'll see labels like `app=httpd_app` that were defined in the http.yml file.

**Query Prometheus using labels:**

Go to the Prometheus web UI and run these queries:

**1. Filter by namespace:**

```promql
container_cpu_usage_seconds_total{namespace="http"}
```

**2. Filter by app label:**

```promql
kube_pod_info{namespace="http", pod=~"httpd-deployment-.*"}
```

**3. Count pods by namespace:**

```promql
count(kube_pod_info{namespace="http"})
```

**4. CPU usage for specific workload:**

```promql
sum(rate(container_cpu_usage_seconds_total{namespace="http",pod=~"httpd.*"}[5m]))
```

### Best Practices for Labels

**DO:**
- Use consistent naming: `environment`, `team`, `app`
- Keep cardinality low (avoid user IDs, timestamps)
- Add labels at deployment time in manifests
- Use labels for filtering, not for high-dimensional data

**DON'T:**
- Use unique values per request (request_id)
- Include timestamps or counters in labels
- Create labels with thousands of unique values
- Use labels for data that changes frequently

> Note: The http.yml manifest in this lab includes labels like `app: httpd_app`. In production, you'd add `environment: prod`, `team: platform`, `version: v1.0`, etc.

### Monitor in Grafana

Now view that namespace in Grafana. Go to the dashboard:

- Kubernetes / Compute Resources / Workload

Then, change the namespace dropdown to *http*.

You should see the CPU usage (and quota) for that namespace.

Add a threshold for alerts:

- On the CPU Usage panel click the edit (3 dots) button and select **edit** or just press `e`.
- Scroll down to Thresholds
- Add one at 80% (or T1 level 2 absolute).
- Change from Absolute to Percentage.
- Set "Show Thresholds" as "lines".
- Apply it to the panel.

Run a couple tests against the web server service (from within a worker in the cluster or from without). For example:

```bash
ab -n 1000000 -c 1000 http://<ip_address>:32321/index.html
```

> Note: You might need to install Apache Utilities if you didn't already at the controller. `sudo apt install apache2-utils`.

View the change in the Grafana dashboard. Keep in mind that there might be a delay. You can also configure any thresholds that you set to set off alerts as well. (Depending on the resources in your cluster you might need to select lower options, for example `ab -n 10000 -c 100`.)

> Note: You can see this activity from a Linux point of view by opening the `top` program on the K8s controller and looking for the *ab* or *ksoftirqd* process.

Also check out the following dashboards:

- Kubernetes / Compute Resources / Namespaces (Workloads)
  - Check prometheus and http
- Kubernetes / Compute Resources / Cluster
- Alertmanager / Overview
  - Check out the Notificatins area. Good for alerts when there is spamming!

---
You can use several other built-in dashboards to further monitor the service, pods, namespace, and so on. This is going to work in essentially the same manner for other applications. However, if you are creating your own applications, you will often need to configure the scraping of metrics as well.

## ♾️ Now you are monitoring Kubernetes! Great work! 

---

## Extra Credit

- Solo Grafana install with Helm: https://grafana.com/docs/grafana/latest/setup-grafana/installation/helm/
- Consider these other tools for stress testing Kubernetes: 
  - K6, JMeter, Locust, Siege, Gatling, Kube-burner, and PowerfulSeal.

## Extra Extra Credit

- You might also want to monitor a Kubernetes cluster *externally* from a stand-alone Prometheus server. See this lab for details!