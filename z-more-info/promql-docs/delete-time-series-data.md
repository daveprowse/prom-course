# Delete Time-Series Data

As you are doing your tests, you may find that you have a lot of results that skew your tests. After a time, you might decide to clear those scrape results from Prometheus. This would also be known as deleting time-series data, or resetting your metrics.

This document shows three ways to do this, but use caution! And do not attempt this on production systems.

> Note: You can't selectively clear - you have to delete all TSDB data.

## Option 1 - Delete All Data  (DANGEROUS!)
```bash
sudo systemctl stop prometheus
sudo rm -rf /var/lib/prometheus/metrics2/*
sudo systemctl start prometheus
```

Data will rebuild immediately as Prometheus starts scraping again.

---

## Option 2 - Use Admin API

Add flag to service file:
```bash
sudo nano /lib/systemd/system/prometheus.service
```

Add `--web.enable-admin-api` to ExecStart:
```
ExecStart=/usr/bin/prometheus $ARGS \
--config.file /etc/prometheus/prometheus.yml \
--storage.tsdb.path /var/lib/prometheus/metrics2 \
--web.enable-admin-api
```

Reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart prometheus
```

Delete specific series:
```bash
curl -X POST -g 'http://localhost:9090/api/v1/admin/tsdb/delete_series?match[]={job="prometheus"}'
```

---

## Option 3 - Wait for Automatic Expiration

Prometheus has default retention of 15 days. Old data automatically expires.

---

**For lab purposes:** Use Option 1 (full reset) - it's cleanest and fastest.

**Warning:** Option 1 deletes ALL metrics, not just HTTP requests.