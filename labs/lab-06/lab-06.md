# ⚙️ Lab 06 - Installing the Alertmanager

The Alertmanager is an extension in Prometheus that allows you to create rules and alerts that can notify you in the case of an event. 

The alertmanager tool is used to notify persons (or systems) of important happenings: downed systems, heavy CPU or disk usage, potential security alerts, and more.

## Install the alertmanager

Let's install the alertmanager to the main Prometheus monitoring system.

There is an included script `alertmanager-install.sh` in this directory that will install the alertmanager and run it as a service automatically.

To use the script, set the permissions to executable, and run the script with sudo.

`chmod +x alertmanager-script.sh`

`sudo ./alertmanager-script.sh`

When you are done, check the installation, service, and web connection:

`alertmanager --version`

`systemctl status alertmanager`

`http://<ip_address>:9093` and Status

> Note: Make sure that port 9093 is open on your system and firewall.

## Configure Prometheus to Talk to Alertmanager

Now, make sure that Prometheus sends alerts to Alertmanager. 

Do this in `/etc/prometheus/prometheus.yml`.

Find the alerting section. 

Uncomment the `- alertmanager:9093` line and change it to:

```
- <ip_address>:9093
```

This will be the address of your Prometheus server. If it is local, you can use `localhost` or `127.0.0.1` instead of `<ip_address>`.

---

**Manual Installation**

If you would like to install it manually, you can do it from the following links:

- https://prometheus.io/download/
- https://github.com/prometheus/alertmanager

Keep in mind that you install it manually, you will have to run it manually with the following command:

`./alertmanager`

## That's it! Great Work! 😀

