# ⚙️ Lab 14 - Installing an Apache Exporter

In this lab we will:

- Enable Apache mod_status
- Install the Apache Exporter
- Configure Prometheus to scrape Apache metrics
- Query Apache metrics from the Web UI
- Import the Apache Grafana Dashboard

## Prerequisites

Apache2 must be installed and running on the system to be monitored.

```bash
systemctl status apache2
```

If it is not installed:

```bash
sudo apt install apache2 -y
sudo systemctl --now enable apache2
```

---

## Part 1 - Configuring the Remote System and Installing the Apache Exporter

### Enable Apache mod_status

The Apache Exporter scrapes metrics from Apache's built-in `mod_status` module. This must be enabled first.

**1. Check the module's status:**

```bash
sudo a2enmod status
```

If not enabled, follow the next step to enable it.

**2. Configure mod_status:**

Open the Apache status configuration file:

```bash
sudo nano /etc/apache2/mods-enabled/status.conf
```

Make sure the following block exists and is uncommented:

```apache
<Location "/server-status">
    SetHandler server-status
    Require local
</Location>
```

> Note: `Require local` restricts access to localhost only, which is appropriate for scraping.

**3. Restart Apache:**

```bash
sudo systemctl restart apache2
```

**4. Verify mod_status is working:**

```bash
curl http://localhost/server-status?auto
```

You should see a plain-text response with Apache statistics. If you see output, mod_status is working correctly.

> Note: If you get a 403 Forbidden error, check that `Require local` is set correctly in the status.conf file.

---

### Install the Apache Exporter

The included script `apache-exporter-install.sh` will install the Apache Exporter and run it as a service.

Set the script to executable and run it:

```bash
chmod +x apache-exporter-install.sh
sudo ./apache-exporter-install.sh
```

When complete, verify the installation:

```bash
apache_exporter --version
systemctl status apache_exporter
```

The exporter listens on **port 9117** by default.

Verify the metrics endpoint is available:

```bash
curl http://localhost:9117/metrics
```

You should see a long list of metrics beginning with `apache_`.

> Note: This exporter can be found at: https://github.com/Lusitaniae/apache_exporter

---

### Configure Prometheus

On the Prometheus server, add the Apache Exporter as a scrape target.

Edit `/etc/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'apache'
    static_configs:
      - targets: ['<ip_address>:9117']
```

> Note: Replace `<ip_address>` with the IP address of the system running the Apache Exporter. If running on the same system as Prometheus, use `localhost`.

Reload Prometheus:

```bash
sudo systemctl reload prometheus
```

Verify the target is up:

Go to Prometheus Web UI > Status > Target Health. You should see `apache` listed with a status of **UP**.

**Excellent! Take a break and then continue with Part 2!**

---

## Part 2 - Query Apache Metrics

Access the Prometheus Web UI at `http://localhost:9090` and run the following queries.

**1. Apache up status:**

```promql
apache_up
```

Should return `1` if the exporter is successfully scraping Apache.

**2. Total accesses:**

```promql
apache_accesses_total
```

Total number of HTTP requests Apache has handled.

**3. Request rate (per second):**

```promql
rate(apache_accesses_total[5m])
```

HTTP requests per second over the last 5 minutes.

**4. Total bytes transferred:**

```promql
apache_sent_kilobytes_total
```

Total kilobytes sent by Apache.

**5. Workers status:**

```promql
apache_workers
```

Shows the number of Apache worker processes by state (busy, idle).

**6. Busy workers:**

```promql
apache_workers{state="busy"}
```

Number of workers currently handling requests.

**7. CPU load:**

```promql
apache_cpuload
```

Current CPU load of the Apache process.

### Generate Traffic

To see more interesting metrics, generate some HTTP traffic:

```bash
for i in {1..500}; do curl http://localhost/index.html > /dev/null 2>&1; done
```

Re-run the queries above and view in Graph mode to see the changes.

Or use the Apache Benchmark tool for a heavier load:

```bash
ab -n 1000000 -c 100 http://localhost/index.html
```

---

### Import the Grafana Dashboard

A pre-built dashboard is available for the Apache Exporter.

**Dashboard ID:** `3894`

**Import steps:**

1. In Grafana, go to **Dashboards > New > Import**
2. Enter ID: `3894`
3. Click **Load**
4. Select your Prometheus datasource
5. Click **Import**

You should now see Apache metrics visualized across multiple panels including request rate, bytes transferred, worker status, and CPU load.

Run the load tests in the previous section to show actual data!

## 💪 GREAT WORK! 💪**

---

## Troubleshooting

**`apache_up` returns 0:**

The exporter is running but cannot connect to Apache's mod_status page.

Check:
- mod_status is enabled: `apache2ctl -M | grep status`
- The status URL is accessible: `curl http://localhost/server-status?auto`
- Apache is running: `systemctl status apache2`

**Only seeing `apache_up` and `apache_cpuload`:**

Make sure the scrape URI includes `?auto`:

```bash
curl http://localhost/server-status?auto
```

Without `?auto`, Apache returns HTML instead of plain text and the exporter cannot parse it.

**Target shows DOWN in Prometheus:**

- Check firewall: `sudo ufw status` - port 9117 must be open
- Check exporter is running: `systemctl status apache_exporter`
- Check exporter logs: `journalctl -u apache_exporter -n 50`

---

## Extra Credit

**Monitor specific virtual hosts:**

If running multiple virtual hosts, you can point the exporter at a specific server-status URL:

```bash
# In the service file ExecStart line, change:
--scrape_uri=http://localhost/server-status?auto

# To:
--scrape_uri=http://localhost:8080/server-status?auto
```

**Useful PromQL queries:**

```promql
# Average bytes per request
rate(apache_sent_kilobytes_total[5m]) * 1024 / rate(apache_accesses_total[5m])

# Worker utilization percentage
apache_workers{state="busy"} / ignoring(state) (apache_workers{state="busy"} + ignoring(state) apache_workers{state="idle"}) * 100

# Requests per minute
rate(apache_accesses_total[1m]) * 60
```

---

### Links for the Apache Exporter and Apache Dashboard

Credit where credit is due!

**Apache Exporter**

https://github.com/Lusitaniae/apache_exporter

**Apache Dashboard**

https://grafana.com/grafana/dashboards/3894-apache/

---
