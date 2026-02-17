# Key Metrics for Monitoring Linux Systems

Essential PromQL queries for node_exporter metrics.

---

## CPU Metrics

```
node_cpu_seconds_total  # CPU usage by core and mode (idle, system, user, iowait)
node_load1              # System load average over 1 minute
node_load5              # System load average over 5 minutes
node_load15             # System load average over 15 minutes
```

---

## Memory Metrics

```
node_memory_MemAvailable_bytes  # Available RAM in bytes
node_memory_MemTotal_bytes      # Total RAM in bytes
node_memory_SwapFree_bytes      # Free swap space in bytes
node_memory_SwapTotal_bytes     # Total swap space in bytes
```

---

## Disk Metrics

```
node_filesystem_avail_bytes{mountpoint="/"}  # Available disk space on root filesystem
node_filesystem_size_bytes{mountpoint="/"}   # Total disk size on root filesystem
node_disk_io_time_seconds_total              # Total time spent on disk I/O operations
```

---

## Network Metrics

```
node_network_receive_bytes_total   # Total bytes received on network interfaces
node_network_transmit_bytes_total  # Total bytes transmitted on network interfaces
node_network_receive_errs_total    # Total receive errors on network interfaces
node_network_transmit_errs_total   # Total transmit errors on network interfaces
```

---

## System Metrics

```
up                      # Target availability (1 = up, 0 = down)
node_boot_time_seconds  # Unix timestamp of system boot time
node_time_seconds       # Current system time as Unix timestamp
process_open_fds        # Number of open file descriptors
```

---

## Useful Calculated Queries

**CPU usage percentage (100 - idle percentage):**
```
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Memory usage percentage:**
```
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

**Disk usage percentage for root filesystem:**
```
(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100
```

**Network receive rate in MB/s:**
```
rate(node_network_receive_bytes_total[5m]) / 1024 / 1024
```

**Network transmit rate in MB/s:**
```
rate(node_network_transmit_bytes_total[5m]) / 1024 / 1024
```

**System uptime in days:**
```
(time() - node_boot_time_seconds) / 86400
```

---
