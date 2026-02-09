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