# Setup steps for TLS (in brief)

1. Generate cert: `openssl req -x509 -newkey rsa:4096 -keyout node_exporter.key -out node_exporter.crt -days 365 -nodes`
2. Move both files to `/etc/node_exporter/`
3. Copy `.crt` to Prometheus server at `/etc/prometheus/`
4. Update service file, daemon-reload, restart