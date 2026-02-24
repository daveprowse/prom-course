# Testing from within a Kubernetes Prometheus Pod

This document provides commands for testing and exploring capabilities from within a Prometheus pod running in Kubernetes.

## Accessing the Pod

First, get the exact pod name:

```bash
kubectl get pods -n prometheus | grep prometheus
```

Access the Prometheus pod:

```bash
kubectl exec -it -n prometheus prometheus-stable-kube-prometheus-sta-prometheus-0 -- sh
```

> Note: In the field, avoid exec'ing into pods unless absolutely necessary!

---

## Network Connectivity Tests

**Test HTTP/HTTPS connectivity with wget:**

```bash
wget --spider --timeout=5 example.com
wget --spider --timeout=5 google.com
wget --spider --timeout=5 prometheus.io
```

**Download and view a web page:**

```bash
wget -O- example.com
```

**Test specific ports with netcat:**

```bash
# Test if a port is open (timeout after 5 seconds)
nc -zv -w5 example.com 80
nc -zv -w5 example.com 443

# Test connectivity to another pod or service
nc -zv -w5 stable-grafana.prometheus.svc.cluster.local 80

# Listen on a port (if you need to test from another pod)
nc -l -p 8080
```

**Test DNS resolution:**

DNS is tested implicitly when using hostnames with wget or netcat. Successful resolution means DNS is working.

```bash
# This tests both DNS and HTTP
wget --spider prometheus.io
```

---

## System and Network Information

**Check DNS configuration:**

```bash
cat /etc/resolv.conf
```

**View network interfaces (if available):**

```bash
ip addr
ifconfig
```

**Check environment variables:**

```bash
env
```

**View resource limits:**

```bash
ulimit -a
```

**Check why ping fails:**

```bash
cat /proc/sys/net/ipv4/ping_group_range
```

This shows the group ID range allowed to use ping. The Prometheus user is outside this range for security.

**Check running processes:**

```bash
ps aux
```

**View mounted filesystems:**

```bash
df -h
mount
```

---

## Exploring Installed Tools

**List available binaries:**

```bash
ls /bin
ls /usr/bin
ls /usr/local/bin
```

**Check for specific tools:**

```bash
which wget
which nc
which netcat
which curl
which ping
```

**Test if a command exists:**

```bash
command -v wget && echo "wget is installed" || echo "wget not found"
command -v curl && echo "curl is installed" || echo "curl not found"
```

---

## Prometheus-Specific Tests

**Check Prometheus data directory:**

```bash
ls -la /prometheus
ls -la /prometheus/wal
```

**View Prometheus configuration:**

```bash
cat /etc/prometheus/config_out/prometheus.env.yaml
```

**Check Prometheus process:**

```bash
ps aux | grep prometheus
```

**View Prometheus logs (from outside the pod):**

```bash
kubectl logs -n prometheus prometheus-stable-kube-prometheus-sta-prometheus-0 -c prometheus
```

---

## Security and Permissions

**Check current user:**

```bash
id
whoami
```

**Try to become root (will fail):**

```bash
su -
```

Expected result: `su: must be suid to work properly` or command not found.

**Check file permissions:**

```bash
ls -la /prometheus
ls -la /etc/prometheus
```

**Test write permissions:**

```bash
touch /tmp/test.txt
echo "test" > /tmp/test.txt
cat /tmp/test.txt
rm /tmp/test.txt
```

---

## Network Testing Between Pods

**From the Prometheus pod, test connection to Grafana:**

```bash
nc -zv -w5 stable-grafana.prometheus.svc.cluster.local 80
wget --spider http://stable-grafana.prometheus.svc.cluster.local
```

**Test connection to Alertmanager:**

```bash
nc -zv -w5 stable-kube-prometheus-sta-alertmanager.prometheus.svc.cluster.local 9093
```

**Test connection to node-exporter on a node:**

```bash
nc -zv -w5 <ip_address> 9100
wget --spider http://<ip_address>:9100/metrics
```

---

## Useful One-Liners

**Test external connectivity:**

```bash
wget --spider --timeout=5 8.8.8.8 2>&1 | grep -q "connected" && echo "External network OK" || echo "No external access"
```

**Test DNS:**

```bash
wget --spider --timeout=5 google.com 2>&1 | grep -q "connected" && echo "DNS OK" || echo "DNS failed"
```

**Check available disk space:**

```bash
df -h /prometheus
```

**Count WAL segments:**

```bash
ls /prometheus/wal/ | grep -E '^[0-9]+$' | wc -l
```

---

## Why Some Tools Are Missing

The Prometheus container image is deliberately minimal for security and efficiency:

- **No curl**: wget provides similar functionality
- **No ping**: Requires CAP_NET_RAW capability (security restriction)
- **No ssh**: Not needed for containerized workloads
- **No package managers**: Image is immutable

This reduces the attack surface and keeps the container lightweight.

---

## Exit the Pod

When done testing:

```bash
exit
```

---

**Note:** These commands are for testing and learning purposes. In production, avoid exec'ing into pods unless necessary for troubleshooting.
