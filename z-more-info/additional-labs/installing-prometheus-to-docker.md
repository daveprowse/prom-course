# ⚙️ Mini-Lab - Installing Prometheus to Docker

Learn how to deploy Prometheus monitoring in a Docker container on headless systems.

---

## What You'll Build

- Prometheus server running in Docker on port 9091
- Accessible via browser from remote machine
- Runs alongside existing Prometheus installation (if you installed to the Linux VM)

**Time Required:** 10-15 minutes

---

## Prerequisites

- Docker installed (see [Installing Docker](#installing-docker) at end)
- SSH access to PROM1 or PROM2 (or any Linux system)


> Note: We'll use port *9091* instead of the default 9090 because we already have a native Prometheus server on port 9090.

---

## Step 1: Create Prometheus Configuration

SSH to PROM1 or PROM2:
```bash
ssh sa@<ip_address>
```

Create a directory for Prometheus data:
```bash
mkdir -p ~/prometheus-docker
cd ~/prometheus-docker
```

Create `prometheus.yml`:
```bash
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Monitor itself on port 9091
  - job_name: 'prometheus-docker'
    static_configs:
      - targets: ['localhost:9091']
  
  # Monitor native Prometheus on port 9090
  - job_name: 'prometheus-native'
    static_configs:
      - targets: ['localhost:9090']
EOF
```

**Verify:**
```bash
cat prometheus.yml
```

---

## Step 2: Run Prometheus Container
```bash
docker run -d \
  --name prometheus-docker \
  -p 9091:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:latest
```

**Command breakdown:**
- `-d` - Run in background
- `--name prometheus-docker` - Container name
- `-p 9091:9090` - Map container port 9090 to host port 9091
- `-v` - Mount config file
- `prom/prometheus:latest` - Official image

**Verify container is running:**
```bash
docker ps
```

Should show:
```
CONTAINER ID   IMAGE                    STATUS         PORTS
abc123...      prom/prometheus:latest   Up 5 seconds   0.0.0.0:9091->9090/tcp
```

---

## Step 3: Verify with CLI

### Check Health
```bash
# Docker Prometheus
curl -s http://localhost:9091/-/healthy
# Should return: Prometheus is Healthy.

# Native Prometheus (for comparison)
curl -s http://localhost:9090/-/healthy
```

### Query Metrics
```bash
# Check if both Prometheus instances are up
curl -s 'http://localhost:9091/api/v1/query?query=up' | jq .
```

**Should show both targets:**
- `prometheus-docker` on port 9091
- `prometheus-native` on port 9090

---

## Step 4: Access from Remote Browser

### From Your Laptop/Workstation

Open your browser and navigate to:
```
http://<ip_address>:9091
```

**Replace** `<ip_address>` with your actual PROM1/PROM2 IP address.

### Quick Browser Tests

**1. Check Targets Status:**
- Navigate to: **Status → Targets**
- Should see both endpoints as "UP":
  - `prometheus-docker` (localhost:9091)
  - `prometheus-native` (localhost:9090)

**2. Run a Query:**
- Click **Graph** tab
- Enter query: `up`
- Click **Execute**
- Should see 2 results with value = 1

**3. View Metrics:**
- Click **Graph** tab
- Enter query: `process_resident_memory_bytes`
- Click **Execute** then **Graph** tab
- See memory usage over time

---

## Comparing Both Prometheus Instances

You now have TWO Prometheus servers running:

| Instance | Port | Access |
|----------|------|--------|
| **Native** | 9090 | http://10.42.88.1:9090 |
| **Docker** | 9091 | http://10.42.88.1:9091 |

**Try opening both in separate browser tabs!**

---

## Managing the Container

### View Logs
```bash
docker logs prometheus-docker

# Follow logs in real-time (Ctrl+C to exit)
docker logs -f prometheus-docker
```

### Stop/Start/Restart
```bash
# Stop
docker stop prometheus-docker

# Start
docker start prometheus-docker

# Restart
docker restart prometheus-docker
```

### Check Resource Usage
```bash
docker stats prometheus-docker --no-stream
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs for errors
docker logs prometheus-docker

# Verify port is available
sudo netstat -tlnp | grep 9091
```

### Can't Access from Browser

**Check firewall:**
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 9091/tcp

# CentOS/RHEL
sudo firewall-cmd --list-all
sudo firewall-cmd --add-port=9091/tcp --permanent
sudo firewall-cmd --reload
```

**Verify container is listening:**
```bash
# From PROM1/PROM2
curl http://localhost:9091/-/healthy

# Check port binding
docker port prometheus-docker
```

**Test from your workstation:**
```bash
# Should return "Prometheus is Healthy."
curl http://10.42.88.1:9091/-/healthy
```

### Configuration Errors
```bash
# Validate config
docker exec prometheus-docker promtool check config /etc/prometheus/prometheus.yml

# View current config
docker exec prometheus-docker cat /etc/prometheus/prometheus.yml
```

---

## Cleanup

Remove Docker Prometheus (keeps native Prometheus):
```bash
# Stop and remove container
docker stop prometheus-docker
docker rm prometheus-docker

# Remove config directory
rm -rf ~/prometheus-docker

# Verify native Prometheus still running
curl http://localhost:9090/-/healthy
```

---

## Installing Docker

### Ubuntu/Debian (PROM1/PROM2)
```bash
# Update package index
sudo apt update

# Install dependencies
sudo apt install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group (logout/login required)
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Verify (may need to logout/login first)
docker --version
docker run hello-world
```

### CentOS/RHEL
```bash
# Install dependencies
sudo yum install -y yum-utils

# Add Docker repository
sudo yum-config-manager --add-repo \
  https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Verify
docker --version
```

### Quick Verification
```bash
# Check version
docker --version

# Check service status
sudo systemctl status docker

# Test without sudo (after logout/login)
docker run hello-world
```

**If "permission denied":**
```bash
# Logout and login again for group membership to take effect
exit
ssh sa@10.42.88.1
docker ps  # should work now
```

---

## Lab Complete! 🎉