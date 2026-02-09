# ⚙️ Lab 08 - Alertmanager, External Services, and Grafana

In this lab we will:

- Configure Alertmanager to send alerts to PagerDuty and Slack/Discord.
- Create and test alerts in Grafana.

## Part 1 - Connecting the Alertmanager to External Services

Alertmanager can route alerts to external services for notifications. Let's configure PagerDuty and Slack/Discord.

### Configure PagerDuty Integration

Edit the Alertmanager configuration:

`sudo nano /etc/alertmanager/alertmanager.yml`

> Note: Before making changes to configuration files, remember to make a backup!

In the `receivers:` section, add the PagerDuty receiver:

```yaml
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<your-pagerduty-integration-key>'
```

> Note: Get your integration key from PagerDuty: You will most likely need to create a new service and integrate Prometheus to it. Then, find the Integration Key and copy it to the `service_key:` entry in the `alertmanager.yml` file.

Then, change the `receiver:` line (inside of `route`) from `'web.hook'` to `'pagerduty'`.

Check your cofiguration:

```
amtool check-config /etc/alertmanager/alertmanager.yml
```

Make sure that it says "SUCCESS"

Reload Alertmanager:

`sudo systemctl reload alertmanager`

> Note: If necessary, do a full restart of the service, and the Prometheus service as well.

On the remote system, either stop SSH or poweroff the system. Anything to generate an alert!

Be ready for alerts! Check to make sure they are firing in:

- Prom Web UI: `http://<ip_address>:9090`
- AlertManager UI: `http://<ip_address>:9093`
- PagerDuty website < Prometheus service
- Your phone/email/etc...!

*You may find that PagerDuty will alert you via SMS text before the Prometheus or Alertmanager web UI does!*

> Note: The free tier of Pagerduty has limited SMS messages (approximately 100) but will continue to email you if you run out of SMS. You can disable notification types in the Prometheus service, or globally in Profile > Notification Rules.

Fix the problem! Restart the SSH service on the remote system. Wait a couple of minutes and check it in the Prometheus web UI and Alertmanager web UI. 

Respond to the incident! For example, SMS reply `26` to resolve all. Check it in the PagerDuty web UI.

When you are finished, consider removing the PagerDuty service from the `receiver:` section of `alertmanager.yml` so you won't get any more notifications.

> Note: If you are concerned about retaining a Prometheus integration key, simply remove the Prometheus service from the PagerDuty UI.

### (Optional) Configure Slack/Discord Integration

_**Important!** Slack and Discord can be finicky so I'm adding some examples. However, you might encounter the need for additional configuration._

For Slack, create an Incoming Webhook:

1. Go to https://api.slack.com/apps
2. Create New App > From Scratch
3. Add Incoming Webhooks > Activate
4. Add New Webhook to Workspace
5. Copy the Webhook URL

Edit `/etc/alertmanager/alertmanager.yml`:

```yaml
route:
  receiver: 'slack'
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h

receivers:
  - name: 'slack'
    slack_configs:
      - api_url: '<your-slack-webhook-url>'
        channel: '#alerts'
        title: 'Prometheus Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

For Discord, create a webhook:

1. Server Settings > Integrations > Webhooks > New Webhook
2. Copy Webhook URL
3. Append `/slack` to the Discord webhook URL

```yaml
receivers:
  - name: 'discord'
    slack_configs:
      - api_url: '<your-discord-webhook-url>/slack'
        title: 'Prometheus Alert'
```



> Discord Troubleshooting: To check if your webhook is working properly, use a command such as:
> ```
> curl -H "Content-Type: application/json" -X POST -d '{"text":"Test from curl"}' https://discordapp.com/api/webhooks/<webhook_url>/slack
> ```

> It should show up in the Discord channel.

---

## Part 2 - Using Alerts in Grafana

Grafana can create alerts based on panel queries and send notifications.

### Create SSH Service Alert

1. Go to your Grafana dashboard
2. Click **Alerting** (bell icon) > **Alert rules**
  > Note: Grafana should automatically see the rules from Prometheus, but no "Grafana-managed" rules.
3. Click **+ New alert rule** and name the alert "ssh-alert".

Configure the alert:

**Section 1 - Set query and alert condition:**
- Query: Select your Prometheus data source
- Metric: `node_systemd_unit_state{name="ssh.service", state="active"}`
- Expression: Set **Alert condition/Threshold** to `below < 1`

**Section 2 - Set alert evaluation behavior:**
- Folder: Create new folder "Linux Alerts"
- Evaluation group: Create new "node-alerts" (interval: 1m)
- Pending period: 1m

**Section 3 - Add details:**
- Configure notifications by adding a contact point (the default is fine for this lab).
- Summary: `SSH service is down on {{ $labels.instance }}`
- Description: `SSH service has been inactive for more than 1 minute`

Click **Save and exit**

### Create High CPU Alert

Repeat the process with:

**Query:**
```
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Alert condition/Threshold:** `> 80`

**Alert name:** `High CPU Usage`

**Summary:** `CPU usage above 80% on {{ $labels.instance }}`

### Test the Alerts

**Test SSH Alert:**

Stop SSH service on monitored host:

`sudo systemctl stop ssh`

Wait 1-2 minutes, then check **Alerting > Alert rules**. Status should show **Firing**. Refresh the screen if necessary.

Restart SSH:

`sudo systemctl start ssh`

**Test CPU Alert:**

Generate CPU load on monitored host:

1. Install `stress` program (`sudo apt install stress`)
2. Run command to initiate CPU stress test:

```
stress --cpu 4 -t 80
```

That should be enoug to trigger the alert. If not, you might need to run the program additional times to trigger the alert!

Other options:

- `dd if=/dev/zero of=/dev/null &`
- `for i in {1..4}; do dd if=/dev/zero of=/dev/null & done`

Monitor in Grafana. 

Stop with `Ctrl+C` or `fg` and then `Ctrl+C`.

> Note: You might have to wait several minutes, or restart the server, to show the alert status as normal again.

### View Alert History

**In Grafana UI:**

1. Go to Alerting > Alert rules
2. Find your alert (e.g., "SSH Service Down")
3. Click on the alert name to see details
4. View the State history section showing when it fired/resolved

**Or use Explore:**

1. Go to Explore
2. Query: `ALERTS{alertname="SSHServiceDown"}`
3. Click the blue "Run Query" button to execute it.
4. Shows timeline of alert states

---

**🚀 EXCELLENT WORK! 🚀**

---

## Extra Credit

**Configure Contact Points:**

1. Go to **Alerting > Contact points**
2. Click **+ Add contact point**
3. Select integration type (Email, Slack, PagerDuty, Webhook)
4. Configure and test

**Create Notification Policies:**

1. Go to **Alerting > Notification policies**
2. Edit default policy or create new
3. Route alerts to specific contact points based on labels

**Create a Recording Rule**

Recording rules pre-calculate frequently used queries to improve performance.

1. Add to `/etc/prometheus/rules.yml`:
```yaml
groups:
  - name: cpu_rules
    interval: 30s
    rules:
      - record: instance:cpu_usage:rate5m
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

2. Reload Prometheus:

`sudo systemctl reload prometheus`

3. Verify in Prometheus Web UI:
4. Query: `instance:cpu_usage:rate5m`
5. Use in Grafana:

- Create new panel
- Query: `instance:cpu_usage:rate5m`

This metric updates every 30 seconds with pre-calculated CPU usage

Benefits: Faster queries, reduced load on Prometheus.

---

## Recording Rules Explained:

I didn't spend too much time on recording rules. Here's a little bit more information.

**The Problem**

Complex queries are slow and CPU-intensive. 

Running `100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` on every dashboard refresh taxes Prometheus.

**The Solution**

Recording rules pre-calculate and store the result as a simple metric like instance:cpu_usage:rate5m. Now dashboards just query the pre-calculated value.

**Real-World Benefits**

Example: You have 50 dashboards all calculating CPU usage the same way.

Without recording rule: Prometheus calculates the same complex query 50 times
With recording rule: Prometheus calculates once every 30s, stores it. Dashboards just read the stored value.

**When to use**

- Dashboard queries that run repeatedly
- Complex calculations used across multiple alerts
- High-cardinality aggregations (many instances/labels)

Simple analogy: Instead of manually calculating your bank balance every time you check it, the bank pre-calculates and stores it for you. Much faster.

---