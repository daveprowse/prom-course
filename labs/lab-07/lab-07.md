# ⚙️ Lab 07 - Configuring Alerting Rules

In this lab, we'll configure three alerts in the Prometheus alertmanager. 

> Note: All of the rules used in this lab are also in `rules.yml` in this directory. 

## Configure and View our first Alert

Let's configure a very basic alert. We want to be notified if one of the systems that we are monitoring goes down.

### Configure the Alert

With sudo, create a file in `'etc/prometheus` called `rules.yml` and add the following code:

```yaml
groups:
  - name: node_rules
    rules:
      - alert: host-is-down
        expr: up{job="node"} == 0
```

Save the file.

> Note: If you are running Prometheus manually, save the rules file to wherever you extracted Prometheus.

Now, point to that rules file from the prometheus configuration file.

- Open prometheus.yml
- Find the `rule_files` section.
- Change `first_rules.yml` to `/etc/prometheus/rules.yml` and uncomment it.

Use the promtool to check the syntax of your rules file:

`promtool check rules /etc/prometheus/rules.yml`

Restart the prometheus and alertmanager services:

`sudo systemctl reload {alertmanager,prometheus}`

Check them to make sure they are active:

`systemctl status {alertmanager,prometheus}`

### View the new Alert

Wait about 5 to 10 seconds for everything to come up and access your Prometheus web UI.

Click "Alerts". This should now show the "host-is-down" alert. However, it is green, because none of the hosts we are monitoring have gone down yet!

Now, shut down the remote system that you are monitoring.

While it is shutting down, take a look at the node_exporter dashboard in Grafana. The dreaded **N/A** will rear it's ugly head soon.

Now, view the Alert in the Prometheus web UI again. It should show one firing alert in read. Expand the drop down menu to see the particular host that is down.

😁 This is how we do Prometheus. 😁

## Configure and View our Second Alert

Now let's create an alert tha twill notify us if the SSH server on a remote system has failed.

### Add the Rule

```yaml
- alert: SSHServiceDown
  expr: node_systemd_unit_state{name=~"ssh.service|sshd.service", state="active"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "SSH service is down on {{ $labels.instance }}"
    description: "SSH service has been inactive for more than 1 minute on {{ $labels.instance }}"

```

- Reload the service
- View it in the Prom Web UI
- Shut down SSH on the remote system (or local if only one).
- View the alert again
- Restart the SSH service and verify that the alert stopped firing.

## Configure and View our Third Alert

This time, let's build an alert that will predict when our disk will hit zero empty space (100% full).

### Add the Rule

```yaml
groups:
- name: disk_alerts
  rules:
  - alert: DiskWillFillSoon
    # Predicts if 'free space' will be <= 0 in 4 hours, based on the last 6 hours of data
    expr: predict_linear(node_filesystem_free_bytes{job="node"}[6h], 4 * 3600) <= 0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Disk predicted to be full on {{ $labels.instance }}"
      description: "Based on recent usage, the volume {{ $labels.mountpoint }} will run out of space in less than 4 hours."
```

- Reload the service
- View it in the Prom Web UI

> Note: To get that "predictive" disk alert working in Prometheus, we use the `predict_linear` function. This is much smarter than a static 90% threshold because it looks at the rate of change over time.
> 
> For example, a disk that is 90% full but hasn't changed in a month isn't an emergency. A disk that is 50% full but filling at 10% per hour is an emergency.

## YES! Another lab DONE! 🏁


---

## (Optional Extra Credit) 

Additional alerts:

- Apache/Nginx down: 

  `up{job="apache"} == 0`

- High CPU: 

  ```
  100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
  ```

- High Memory: 

  ```
  (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
  ```

