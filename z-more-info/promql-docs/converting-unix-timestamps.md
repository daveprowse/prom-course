# Converting Unix Timestamps

## Understanding Unix Timestamps

Prometheus uses Unix timestamps (e.g., `1770993159.931`) - seconds since January 1, 1970.

## Conversion Methods

### From CLI

**Basic conversion:**

```bash
date -d @1770993159
```

**From Prometheus API (scalar like time()):**

```bash
date -d @$(curl -s 'http://localhost:9090/api/v1/query?query=time()' | jq -r '.data.result[1]')
```

**From Prometheus API (vector queries):**

```bash
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq -r '.data.result[0].value[0]' | xargs -I {} date -d @{}
```

### In Browser Console

Open browser console (F12 or right-click > Inspect > Console), then:

```javascript
new Date(1770993159 * 1000).toLocaleString()
```

Replace `1770993159` with your actual timestamp.

### Online Tools

https://www.epochconverter.com/

## Display in Expression Browser

**Question:** Can we display human-readable time in the Prometheus Expression Browser?

**Answer:** **No** - Prometheus doesn't have a built-in function to format timestamps as human-readable strings. The expression browser always shows Unix timestamps in Table mode.

**Workarounds:**

- **Use Graph mode**: X-axis shows human-readable dates automatically
- **Use Grafana**: Displays timestamps in readable format
- **Check result externally**: Copy timestamp and convert with `date` command

### Example Workflow

Run in Prometheus:

```promql
timestamp(up)
```

Copy result → Convert:

```bash
date -d @1770993159
```

## Summary

- **CLI**: Use `date -d @<timestamp>` for quick conversion
- **Browser**: Use JavaScript `new Date()` in console
- **Expression Browser**: Always shows raw Unix timestamps in Table mode
- **For readable display**: Use Graph mode or Grafana