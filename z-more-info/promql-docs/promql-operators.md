## PromQL Operators

### Arithmetic Operators

Perform math on metrics:

```
# Calculate memory usage percentage
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100

# CPU time as percentage
rate(node_cpu_seconds_total[5m]) * 100
```

**Available:** `+`, `-`, `*`, `/`, `%`, `^`

### Comparison Operators

Filter or compare values:

```
# Show only servers with high CPU
node_cpu_usage > 80

# Alert on low disk space
node_filesystem_avail_bytes < 1000000000
```

**Available:** `==`, `!=`, `>`, `<`, `>=`, `<=`

`==` is the equal operator that is used to compare between vectors or scalars. 

Example: `node_cpu+seconds_total == 0`

### Logical Operators

Combine conditions:

```
# High CPU AND low memory
(cpu_usage > 80) and (memory_available < 1000000000)

# Either condition
(disk_usage > 90) or (inode_usage > 90)
```

**Available:** `and`, `or`, `unless`
