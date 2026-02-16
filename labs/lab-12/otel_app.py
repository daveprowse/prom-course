#!/usr/bin/env python3

import time
import random
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server

# Set up Prometheus exporter
reader = PrometheusMetricReader()
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

# Create a meter (like a namespace for metrics)
meter = metrics.get_meter("otel_demo_app")

# Create metrics using OTEL API
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total HTTP requests",
    unit="1"
)

active_requests_gauge = meter.create_up_down_counter(
    name="http_active_requests",
    description="Current active HTTP requests",
    unit="1"
)

request_duration = meter.create_histogram(
    name="http_request_duration_seconds",
    description="HTTP request duration",
    unit="s"
)

def handle_request(method, endpoint, status):
    """Simulate handling an HTTP request"""
    print(f"{method} {endpoint} -> {status}")
    
    # Increment active requests
    active_requests_gauge.add(1, {"method": method, "endpoint": endpoint})
    
    # Simulate request processing
    duration = random.uniform(0.01, 0.5)
    start = time.time()
    time.sleep(duration)
    elapsed = time.time() - start
    
    # Record metrics
    request_counter.add(1, {"method": method, "endpoint": endpoint, "status": str(status)})
    request_duration.record(elapsed, {"method": method, "endpoint": endpoint})
    
    # Decrement active requests
    active_requests_gauge.add(-1, {"method": method, "endpoint": endpoint})

def main():
    # Start HTTP server for Prometheus scraping
    start_http_server(8200)
    print("OTEL metrics server started on :8200")
    print("Metrics available at http://localhost:8200/metrics")
    print()
    
    # Simulate traffic
    methods = ["GET", "POST", "PUT", "DELETE"]
    endpoints = ["/", "/api/users", "/api/products", "/health"]
    statuses = [200, 200, 200, 200, 201, 204, 400, 404, 500]  # Mostly success
    
    while True:
        method = random.choice(methods)
        endpoint = random.choice(endpoints)
        status = random.choice(statuses)
        
        handle_request(method, endpoint, status)
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    main()
