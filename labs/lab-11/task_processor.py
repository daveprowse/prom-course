#!/usr/bin/env python3

import time
import random
from prometheus_client import Counter, Gauge, Histogram, Summary, start_http_server

# Define metrics
tasks_processed = Counter(
    'tasks_processed_total',
    'Total number of tasks processed',
    ['status']  # success or failed
)

active_tasks = Gauge(
    'tasks_active',
    'Number of tasks currently being processed'
)

queue_size = Gauge(
    'tasks_queue_size',
    'Number of tasks waiting in queue'
)

task_duration = Histogram(
    'task_duration_seconds',
    'Time spent processing tasks',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

task_latency = Summary(
    'task_latency_seconds',
    'Task processing latency'
)

def process_task(task_id):
    """Simulate task processing"""
    print(f"Processing task {task_id}")
    
    # Increment active tasks
    active_tasks.inc()
    
    # Simulate work (random duration)
    duration = random.uniform(0.1, 3.0)
    start_time = time.time()
    time.sleep(duration)
    elapsed = time.time() - start_time
    
    # Record metrics
    task_duration.observe(elapsed)
    task_latency.observe(elapsed)
    
    # Simulate success/failure (90% success rate)
    if random.random() < 0.9:
        tasks_processed.labels(status='success').inc()
        print(f"Task {task_id} completed successfully in {elapsed:.2f}s")
    else:
        tasks_processed.labels(status='failed').inc()
        print(f"Task {task_id} failed after {elapsed:.2f}s")
    
    # Decrement active tasks
    active_tasks.dec()

def main():
    # Start metrics server
    start_http_server(8100)
    print("Metrics server started on :8100")
    print("Metrics available at http://localhost:8100/metrics")
    
    # Simulate task queue
    task_id = 1
    while True:
        # Simulate varying queue size
        queue_length = random.randint(5, 50)
        queue_size.set(queue_length)
        
        # Process a task
        process_task(task_id)
        task_id += 1
        
        # Brief pause between tasks
        time.sleep(0.5)

if __name__ == "__main__":
    main()