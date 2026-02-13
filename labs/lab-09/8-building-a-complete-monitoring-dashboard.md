# Building a Complete Monitoring Dashboard

In this final lesson, you'll see how all the PromQL concepts come together in a real monitoring dashboard.

Instead of building each panel manually, you'll import a pre-built dashboard that demonstrates all the concepts you've learned.

## What You'll See

The dashboard contains 6 panels that combine concepts from all previous lessons:

1. **Service Health (Success Rate)** - Uses rates and aggregation to show 2xx success percentage
2. **Request Rate Trend** - Shows per-second request rates over time
3. **Predicted Memory** - Uses `predict_linear()` to forecast memory usage 1 hour ahead
4. **Top 5 Endpoints** - Aggregates traffic by handler to show busiest endpoints
5. **Request Latency** - Histogram percentiles (p50, p95, p99) for response times
6. **Target Status** - Shows up/down status for all monitored targets

## Import the Dashboard

**1. Download the dashboard JSON:**

The file is located at: `promql-grafana-dashboard.json`

**2. Access Grafana:**

```
http://localhost:3000
```

(Or your Grafana IP address)

**3. Import the dashboard:**

- Click **Dashboards** (left sidebar)
- Click **New** > **Import**
- Click **Upload dashboard JSON file**
- Select `promql-grafana-dashboard.json`
- Click **Load**

**4. Select datasource: (if necessary)**

- In the dropdown, select your Prometheus datasource
- Click **Import**

**Done!** Your dashboard should now be visible. Take several minutes analyzing the 6 panels. Click on individual panels and use the `v` key to maximize the size of the panel. `v` toggles it back when done.

## Explore the Dashboard

### Generate Traffic for Better Visualization

Run these commands to create activity:

```bash
# Generate mixed traffic
for i in {1..200}; do 
  curl 'http://localhost:9090/metrics' > /dev/null 2>&1
  curl 'http://localhost:9090/api/v1/query?query=up' > /dev/null 2>&1
  curl 'http://localhost:9090/graph' > /dev/null 2>&1
done
```

Wait 15-30 seconds, then refresh the dashboard. You should see:

- **Success Rate**: Should show ~100% (all requests successful)
- **Request Rate**: Multiple colored lines showing traffic per endpoint
- **Predicted Memory**: Gauge showing forecasted memory in 1 hour
- **Top 5 Endpoints**: Pie chart showing traffic distribution
- **Request Latency**: Three lines (p50, p95, p99) showing response times
- **Target Status**: Green "UP" for each monitored target

Try powering the remote system (PROM2) down. Watch the change in the Target Status panel. (It may take 15 seconds or so.)

> Note: If you still have PagerDuty working you should get an alert via SMS/email/etc!

### Understanding the Panels

**Know your shortcuts!**

Remember, press `v` to expand a panel. Press `e` to edit and see/modify the underlying queries. These both work as toggles.

**Panel 1: Service Health**
```promql
sum(rate(prometheus_http_requests_total{code=~"2.."}[5m])) 
/ 
sum(rate(prometheus_http_requests_total[5m])) * 100
```
- Combines: Rates (Part 2), Aggregation (Part 4), Binary operators (Part 5)
- Shows: Percentage of successful requests
- Threshold: Red <95%, Yellow 95-99%, Green >99%

**Panel 2: Request Rate Trend**
```promql
rate(prometheus_http_requests_total[5m])
```
- Combines: Rates (Part 2), Selecting data (Part 1)
- Shows: Requests per second for each handler
- Type: Time series graph

**Panel 3: Predicted Memory**
```promql
predict_linear(process_resident_memory_bytes[30m], 3600) / 1024 / 1024
```
- Combines: Aggregating over time (Part 3), Binary operators (Part 5)
- Shows: Forecasted memory usage 1 hour from now in MB
- Threshold: Green <150MB, Yellow 150-200MB, Red >200MB

**Panel 4: Top 5 Endpoints**
```promql
topk(5, sum by(handler) (rate(prometheus_http_requests_total[5m])))
```
- Combines: Aggregating over dimensions (Part 4), Rates (Part 2)
- Shows: Busiest endpoints by traffic volume
- Type: Pie chart

**Panel 5: Request Latency**
```promql
histogram_quantile(0.50, rate(prometheus_http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(prometheus_http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(prometheus_http_request_duration_seconds_bucket[5m]))
```
- Combines: Histograms (Part 6), Rates (Part 2)
- Shows: Response time percentiles
- Type: Time series with 3 lines (median, p95, p99)

**Panel 6: Target Status**
```promql
up
```
- Combines: Selecting data (Part 1)
- Shows: Current up/down status for each target
- Type: Stat panel with color-coded status

## Customizing the Dashboard

**Change time range:**
- Use time picker in upper right (default: Last 15 minutes)
- Try "Last 1 hour" or "Last 6 hours" to see trends

**Modify refresh rate:**
- Currently set to 10 seconds
- Click refresh dropdown (upper right) to change

**Edit a panel:**
- Click panel title > Edit
- View the PromQL query
- Modify and apply changes
- Click "Save dashboard" to keep changes

**Add your own panel:**
- Click "Add" > "Visualization"
- Select Prometheus datasource
- Enter any PromQL query from previous lessons
- Choose visualization type
- Click "Apply"

## Real-World Applications

This dashboard demonstrates monitoring patterns you'll use in production:

**For web services:**
- Track success rates and latency
- Identify slow endpoints
- Predict capacity issues

**For system monitoring:**
- Monitor memory trends
- Alert before resource exhaustion
- Track service availability

**For capacity planning:**
- Use prediction to plan scaling
- Identify traffic patterns
- Optimize resource allocation

## Key Takeaways

**You've seen how PromQL concepts combine:**

1. **Rates** transform counters into meaningful metrics
2. **Aggregation** summarizes across instances and time
3. **Histograms** reveal performance distributions
4. **Prediction** enables proactive monitoring
5. **Binary operators** create complex calculations
6. **Selectors** filter precisely what you need

**Single queries are building blocks** - Real monitoring combines them into dashboards that tell the complete story of your infrastructure health.

---

**🏁 CONGRATULATIONS! 🏁**

You've completed the PromQL lab series and can now:
- Write effective PromQL queries
- Build monitoring dashboards
- Create alerts that matter
- Understand system performance at a glance

**Next steps:**
- Create custom dashboards for your own services
- Set up alerts in Prometheus rules.yml
- Share dashboards with your team
- Continue learning advanced PromQL patterns

Remember: You are awesome!
