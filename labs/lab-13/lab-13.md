# ⚙️ Lab 13 - Monitoring Linux

Now let's get into some more Linux monitoring with Prometheus.

In this lab we will:

- Install the node_exporter Grafana Dashboard
- Test against nodes and analyze the results
- Install an Apache Exporter

> Note: This is a large lab. Take it slow, and take breaks as necessary.

## Part 1 - Use the node_exporter Grafana Dashboard

Let's work with the node_exporter dashboard for Grafana into our main Prometheus monitoring system.

### Configure prometheus.yml

First, let's configure Prometheus to recognize a new job called `node`.

Add the following job:

```yml
  - job_name: node
    static_configs:
      - targets: ['<ip_address>:9100']
```

> Note: We could use the previous job (remote-systems) where Prometheus was scraping from the node_exporter, but I'd like to keep the jobs separate to avoidd confusion.

Restart the prometheus service.

### Import the node_exporter Dashboard

Now, let's import the node_exporter Dashboard.
This is a pre-built, readily available, dashboard available at:

https://grafana.com/grafana/dashboards/1860-node-exporter-full/

You just need to copy the ID (or URL) from the website over to a new Grafana dashboard on your system. Copy the ID to your clipboard now.

On your main Prometheus monitoring system:

- Click on Dashboards
- Click New, then Dashboard.
- Click "import dashboard".
- Paste in the dashboard ID and click "Load".

  > Note: at the time of this writing, the ID is 1860.

- Select a name for the dashboard.
- Select the Prometheus data source. This should be *prometheus-1*.
- Click "Import".

You should now see the new dashboard but it might not show any metrics until we configure it.

### Configure the Dashboard

In Grafana, modify the following:

- Datasource = prometheus
- Job = node
- Host = *whatever host you want to monitor!*

> Note: Refresh the browser if the new job doesn't show up.

At this point you should see real metrics for the host you are monitoring.

You might see high CPU usage. Change the time range to something shorter, for example 5 minutes.

> Note: If you are doing this locally - meaning that you are running everything on one system, you may also see that the CPU is more busy than usual. Consider doing your testing on secondary systems.

Configure the dashboard as you like. Click and drag line graphs; edit, or delete individual gauges, etc...

However, if you make any changes to the configuration of the dashboard, be sure to SAVE them as a different dashboard name! This way, you have the original to reference later.

---

## Part 2 - Testing and Analyzing Nodes

Time to do some testing so that we can simulate server usage and view those results in the Grafana dashboard.

### dd Test

First, let's simulate CPU usage. On the host to be monitored, run the following command:

`dd if=/dev/zero of=/dev/null &`

This command will copy "zero" to absolutely nowhere. This process will utilize one of the CPU cores of the system. The ampersand (&) runs the process in the background (forks it).

Now go to the Grafana dashboard and view the *CPU Busy* gauge and the *CPU Basic* graph. You should see something to the effect of 25% CPU usage. (Could be more or less depending on your system. Run more `dd` commands to simulate additional CPU usage.)

To stop the test, type the `fg` command to bring the process back to the foreground, then press `Ctrl + C`. That will terminate the test.

> Note: If that doesn't work, use the kill command or top to terminate the `dd` command process. You will have noted that the PID was listed when you first began the `dd` command.

Now view the dashboard again. After a short delay you should see that the CPU usage has gone back down to normal. Refresh the dashboard if necessary.

### Download Test

Download a large file. For example, get a current Ubuntu .iso image. 

`wget https://releases.ubuntu.com/noble/ubuntu-24.04.4-desktop-amd64.iso`

> Note: If the link above doesn't work, find a newer one from here: https://releases.ubuntu.com/.

As the file is downloading, go back to the dashboard, scroll down, and look at the *Network Traffic Basic* graph. It should show the amount of data that is being transmitted per second. (For example, 200 Mb/s.) Refresh the dashboard if necessary. It could take 15-30 seconds to see results. Also, consider changing the timeframe dropdown to 5 minutes.

You will also see the Root FS Used gauge go up. That's because the Ubuntu .iso image is quite big!

### Apache ab Test

Install the Apache web server to the system to be monitored.

`sudo apt install apache2 -y`

Check it to make sure it is active and running:

`systemctl status apache2`

If not, enable and run the Apache service:

`sudo systemctl --now enable apache2`

If you have more than one system, install the Apache Utilities to the monitoring system.

`sudo apt install apache2-utils -y`

On the monitoring system, run the `ab` command to simulate HTTP queries to the second system (the one to be monitored). For example:Why re-create the wheel? (Or gauge as the case may be :) )

`ab -n 1000000 -c 100 http://10.42.88.2:80/index.html`

> Note: you could use any working web server on the remote system.

Go to the main monitoring system's Grafana dashboard and view the *CPU Busy* and *Sys Load* gauges (as well as the *CPU Basic* graph). These should start spiking very quickly. If it peaks to 100% and won't lessen, consider changing the `-n` parameter to something less.

> Note: If you are not receiving results, change your time frame to a minute or less and/or refresh the dashboard.

Also note the Network Traffic graph, this will show that the remote system is *transmitting* data (back to the monitoring system).

To really flood the CPU, try increasing the options:

`ab -n 10000000 -c 1000 http://10.42.88.2:80/index.html`

While that is a good test of the system load, it doesn't really test the Apache web server itself. That is for later!

> **IMPORTANT!** Keep in mind that these were only tests. Real-world data may look different!

## Great work! 😁

---

## More Information

### Label Strategy

```yaml
scrape_configs:
  - job_name: 'linux-nodes'
    static_configs:
      - targets: ['10.42.88.2:9100', '10.42.88.3:9100']
        labels:
          environment: 'production'
          role: 'webserver'
          datacenter: 'us-east'
```

**Benefits:**

- Filter by environment/role in queries
- Aggregate across similar systems
- Route alerts appropriately

## Metric Retention

Configure retention based on needs:
```yaml
# In prometheus.yml or via command-line flag
storage:
  tsdb:
    retention.time: 15d  # Keep 15 days of data
```

**Guidelines:**

- Development: 7-15 days
- Production: 30-90 days
- Long-term: Use remote storage (Thanos, Cortex)


-------------------------------------------------

