# ⚙️ Lab 02 - Metrics versus Logs and Traces

In this lab we will:

- Show how to view metric data from the command line.
- Use the Prometheus query log.

## Analyze Metrics in the Command Line

So far we have run our queries from within the Web UI. But you can also do it from the command line. 

> Note: The following should work locally or remotely.

First, open up the terminal on your Prometheus server.

Enter this basic query:

```
curl http://localhost:9090/metrics
```

That should give you a list of the available metrics to you. *Too many to count!*

Narrow the list! For example:

```
curl http://localhost:9090/metrics | grep "process_resident"
```

This should give you a short list - only two. One is a **HELP** metric that describes what the metric is. The other is the actual metric (preceeded by **TYPE**), in this case - a gauge.

> Note: Using `grep` in the command line is just one way to search for the metric you need. But there are others! Use the tool that works best for you.

> Note: You can use `127.0.0.1` in place of `localhost` if you wish. You can also connect to the server remotely. For example, I would connect to my Prometheus server from my workstation using it's IP: `10.42.25.1`. 

Now let's show an actual query of a metric using `curl`.

```
curl 'http://localhost:9090/api/v1/query?query=up'
```

This command accesses the metrics API section of the Prometheus server. This command should respond with a what looks like a good deal of information, but at the end it should show the current value of the metric, 1, which means the server is up.

You can do this with any metric name in Prometheus. Just replace "up" with the metric name.

Try another, based on our previous filtered search:

```
curl 'http://localhost:9090/api/v1/query?query=process_resident_memory_bytes'
```

This measures the amount of RAM that the Prometheus server is using. In the "value" field you are looking for the second number. It will probably be in the neighborhood of 100 MB.

The way that this information is displayed is machine-readable, not quite human readable. To make it more human readable try it again but pipe it to jq. For example:

```
curl 'http://localhost:9090/api/v1/query?query=process_resident_memory_bytes' | jq
```

Now it's a lot easier to read the fields!

> Note: If you don't have jq, you can install it easily with `sudo apt install jq`. 

> Note: More information on the HTTP API can be found here: https://prometheus.io/docs/prometheus/latest/querying/api/

👍 Excellent work!

## Use the Prometheus Query Log

While Prometheus is not known as a *logging* observability tool per se, it can do some logging anyway! Let's set it up.

### Modify the prometheus.yml configuration file

You will add a line that tells Prometheus where to store the logging file (which will be called query.log).

1. Open `/etc/prometheus/prometheus.yml` with sudo.
2. After the `evaluation_interval` line, add the following:

    ```
    query_log_file: /var/lib/prometheus/query.log
    ```

    > Note: This lab is based on the scripted installation of Prometheus. However, the data directory can vary depending on your installation. Modify it as necessary. If you are running Prometheus statically, use `/prometheus/query.log` or store the file in the `./data` directory wherever you copied the Prometheus binary to. 

3. Save and close the configuration file.
4. Restart Prometheus
   
   ```
   sudo systemctl restart prometheus
   ```

Now look in `/var/lib/prometheus`. It should have a file called `query.log`.
   

### Verify that the Query Log is Functioning

Prometheus should have now generated a `query.log` file. However, it won't be populated until you start making some queries!

Let's run a query that we did previously:

```
curl 'http://localhost:9090/api/v1/query?query=process_resident_memory_bytes' | jq
```

Now, retun back to your query.log file and run the following command:

```
cat query.log | jq
```

This should display all of the log information for our query. Take a minute or two to analyze the information. You will note a few things:

- A timestamp for exactly when the query was done.
- The type of query (in this case - INFO).
- Exactly how long it took for the query to complete.
- The API path and method of the query.

You can also verify if the query log is enabled - with a *query*!

```
curl 'http://localhost:9090/api/v1/query?query=prometheus_engine_query_log_enabled' | jq
```

Remember, look to the second number in the "value" field. It should be set to "1", meaning querying is enabled. 

And since this was another query that we ran, it should show up in the `query.log` file as "promql query logged". 

### Disable the Query Log

For now, let's disable the query log. This will save on processing power.

Comment out the query line in the prometheus.yml file:

`# query_log_file: /var/lib/prometheus/query.log`

and restart the Prometheus server:

`sudo systemctl restart prometheus`

✅ That's it! Great job!

---

## Extra Credit

You can also discern how many queries have failed so far:

```
curl 'http://localhost:9090/api/v1/query?query=prometheus_engine_query_log_failures_total' | jq
```

Hopefully, yours will show a value of "0".

---

If you are running Prometheus manually (with no service), and you are trying to enable the query log, you would either need to shut down the server and start it again manually, or *reload* the Prometheus configuration. 

To reload the configuration, you would need to start the Prometheus server with the `--web.enable-lifecycle` flag.

Then, you can reload the configuration with a command such as:
   
   ```
   curl -X POST http://127.0.0.1:9090/-/reload
   ```

This way, you don't have to *restart* the entire Prometheus server - something we try to avoid in the field. 

---

You could also apply this method if you have Prometheus running as a service as well. For example, in our scripted installation, the service file was created here:

`/lib/systemd/system/prometheus.service`

It should look similar to this:

```
[Unit]
Description=Monitoring system and time series database (Prometheus)
Documentation=https://prometheus.io/docs/introduction/overview/ man:prometheus(1)
After=time-sync.target

[Service]
Restart=on-failure
User=prometheus
Group=prometheus
ExecStart=/usr/bin/prometheus $ARGS \
--config.file /etc/prometheus/prometheus.yml \
--storage.tsdb.path /var/lib/prometheus/metrics2
ExecReload=/bin/kill -HUP $MAINPID
TimeoutStopSec=20s
SendSIGKILL=no

[Install]
WantedBy=multi-user.target
```

To add web-enable, you could add the following flag (or argument) to the ExecStart section:

`--web.enable-lifecyle`

Be sure to escape all lines (with `\`) except for the last line in ExecStart. So for example, your ExecStart section might look like this:

```
ExecStart=/usr/bin/prometheus $ARGS \
--config.file /etc/prometheus/prometheus.yml \
--storage.tsdb.path /var/lib/prometheus/metrics2 \
--web.enable-lifecycle
```

> Note: There are several instances where you would *not* want web.enable. Keep this in mind!

---

Alternative method: You could reload without the lifecycle API (web.enable). This would be done by finding the Prometheus process ID and the sending the SIGHUP signal to it.

`pgrep prometheus`

Find out the process ID (PID), then:

`kill -HUP <prometheus_pid>`

> **!! USE WITH CAUTION !!**

---

**😁 FANTASTIC!! 😁**

---