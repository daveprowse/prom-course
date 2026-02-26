# Port Reference - Prometheus Course

## Standard Prometheus Stack Ports

| Port | Service | Used In |
|------|---------|---------|
| 9090 | Prometheus Server | Lessons 2-3, all labs |
| 9093 | Alertmanager | Lesson 8, Labs 6-8 |
| 3000 | Grafana | Lesson 7, Lab 5 |
| 9100 | node_exporter | Lesson 6, Labs 4, 11, 13-15 |
| 9117 | apache_exporter | Lesson 11, Lab 14 |

## Application/Lab Ports

| Port | Application | Used In |
|------|-------------|---------|
| 8000 | Instrumented Web Server | Lesson 10, Lab 10 |
| 8100 | Task Processor | Lesson 10, Lab 11 |
| 8200 | OpenTelemetry App | Lesson 10, Lab 12 |
| 8089 | Python HTTP Test Server | SLO Testing (Extra Credit) |
| 8300 | Payment Processor | Practice Question 15 Lab |
| 8350 | API Simulator | Practice Question 13 Lab |
| 9999 | Test Metrics Endpoint | Practice Question 14 Lab |

## Kubernetes Ports (when applicable)

| Port | Service | Used In |
|------|---------|---------|
| 16443 | Kubernetes API Server | Lesson 12, Labs 15-16 |
| Various NodePorts | Prometheus/Grafana in K8s | Lesson 12, Labs 15-16 |

## Notes

- All ports are defaults and can be changed if conflicts occur
- Kubernetes NodePorts are dynamically assigned (typically 30000-32767 range)
- Lab ports (8000-8350, 9999) are chosen to avoid conflicts with standard services