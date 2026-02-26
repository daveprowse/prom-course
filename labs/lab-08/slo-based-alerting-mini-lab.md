# ⚙️ Mini-Lab: SLO-Based Alerting

Quick introduction to alerting based on Service Level Objectives instead of the arbitrary thresholds that we've shown up to this point.

**Time:** 5-10 minutes

---

## The Concept

**Old way (arbitrary):**
```promql
error_rate > 0.05  # Why 5%?
```

**New way (SLO-based):**
```promql
burn_rate > 10  # Based on error budget
```

**The difference:** SLO alerts are based on customer promises (SLAs), not guesses.

---

## Quick Example

**Your SLO:** 99.9% of requests succeed (common target)

**Error budget:** 0.1% failures allowed per month

**Burn rate:** How fast you're consuming that budget
- 1x = normal (will last 30 days)
- 10x = critical (budget gone in 3 days)

---

## Hands-On: Create an SLO Alert

**1. Create a recording rule for your SLI**

Create a `rules` directory inside of `/etc/prometheus`

Now create `/etc/prometheus/rules/slo.yml`:

```yaml
groups:
  - name: slo
    interval: 30s
    rules:
      - record: http:availability:sli
        expr: |
          sum(rate(prometheus_http_requests_total{code=~"2.."}[5m]))
          /
          sum(rate(prometheus_http_requests_total[5m]))
```

This calculates request success rate.

> Note: We are using the Prometheus server's built-in web server because we don't have any other web servers running yet.

**2. Add a burn rate alert**

Add to the same file:

```yaml
  - name: slo_alerts
    rules:
      - alert: HighErrorBudgetBurn
        expr: (1 - http:availability:sli) / (1 - 0.999) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Burning error budget 10x faster than sustainable"
```

**What this means:**
- SLO target: 99.9% (0.999)
- Current success rate: `http:availability:sli`
- If burning budget >10x normal rate → alert

Check the rules syntax:

```bash
promtool check rules /etc/prometheus/rules/slo.yml
```

Verify that your syntax is correct before you proceed.

**3. Load the rules**

Edit `prometheus.yml`:

```yaml
rule_files:
  - "rules/slo.yml"
```

Check the configuration syntax:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

> Note: This will also check all rules files that are listed in the configuration. 

Restart:

```bash
sudo systemctl restart prometheus
```

**4. Verify**

Prometheus UI → Alerts → Look for `HighErrorBudgetBurn`

Query the SLI:
```promql
http:availability:sli
```

Should show a 1 or ~0.999 if healthy.

> Note: To actually trigger the alarm we would need a web server that actually tracks bad connections. See [Testing Your SLO Alert](../../z-more-info/additional-labs/testing-your-slo-alert.md) for a short lab on how to do this. 

---

## Why This Matters

**Traditional alert:**
- "Error rate > 5%" 
- Why 5%? Arbitrary!

**SLO-based alert:**
- "Burning budget 10x faster than allowed"
- Based on customer promise (99.9% SLO)
- Alerts when SLA is actually at risk

**Result:** Fewer false alarms, more meaningful alerts.

---

## Key Takeaway

**The SLO approach:**
1. Define what good service looks like (SLI = success rate)
2. Set a target (SLO = 99.9%)
3. Calculate error budget (0.1% failures allowed)
4. Alert when burning budget too fast (burn rate)

**For production:** Use tools like Sloth to generate multi-window burn rate alerts automatically.

**Learn more:** Google SRE Book - https://sre.google/sre-book/service-level-objectives/

## 😀 FANTASTIC! 
