# ⚙️ Lab 08 - Alertmanager, External Services, and Grafana

In this lab we will:

- Configure Alertmanager to send alerts to PagerDuty and Slack/Discord.
- Create and test alerts in Grafana.

## Part 1 - Connecting the Alertmanager to External Services

Alertmanager can route alerts to external services for notifications. Let's configure PagerDuty and Slack.

### Configure PagerDuty Integration

Edit the Alertmanager configuration:

`sudo nano /etc/alertmanager/alertmanager.yml`

Add PagerDuty receiver:

```yaml
route:
  receiver: 'pagerduty'
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h

receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<your-pagerduty-integration-key>'
```

> Note: Get your integration key from PagerDuty: Services > Service Directory > Select Service > Integrations > Add Integration > Prometheus

Reload Alertmanager:

`sudo systemctl reload alertmanager`

### Configure Slack/Discord Integration

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

> Note: Discord webhooks are compatible with Slack format.

Reload Alertmanager:

`sudo systemctl reload alertmanager`

### Test the Configuration

Trigger an alert (stop a monitored service):

`sudo systemctl stop ssh`

Wait 1-2 minutes and check your external service for the alert.

Restart the service:

`sudo systemctl start ssh`

---

## Part 2 - Using Alerts in Grafana

Grafana can create alerts based on panel queries and send notifications.

### Create SSH Service Alert

1. Go to your Grafana dashboard
2. Click **Alerting** (bell icon) > **Alert rules**
3. Click **+ Create alert rule**

Configure the alert:

**Section 1 - Set query and alert condition:**
- Query: Select your Prometheus data source
- Metric: `node_systemd_unit_state{name="ssh.service", state="active"}`
- Expression: Set **Threshold** to `B < 1`

**Section 2 - Set alert evaluation behavior:**
- Folder: Create new folder "Linux Alerts"
- Evaluation group: Create new "node-alerts" (interval: 1m)
- Pending period: 1m

**Section 3 - Add details:**
- Alert name: `SSH Service Down`
- Summary: `SSH service is down on {{ $labels.instance }}`
- Description: `SSH service has been inactive for more than 1 minute`

Click **Save and exit**

### Create High CPU Alert

Repeat the process with:

**Query:**
```
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Threshold:** `B > 80`

**Alert name:** `High CPU Usage`

**Summary:** `CPU usage above 80% on {{ $labels.instance }}`

### Test the Alerts

**Test SSH Alert:**

Stop SSH service on monitored host:

`sudo systemctl stop ssh`

Wait 1-2 minutes, then check **Alerting > Alert rules**. Status should show **Firing**.

Restart SSH:

`sudo systemctl start ssh`

**Test CPU Alert:**

Generate CPU load on monitored host:

`dd if=/dev/zero of=/dev/null &`

Monitor in Grafana. Stop with:

```bash
fg
Ctrl+C
```

### View Alert History

Go to **Alerting > Alert rules** to see:
- Current state (Normal, Pending, Firing)
- When alerts fired
- Alert duration

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