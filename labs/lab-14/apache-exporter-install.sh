#!/bin/bash

#########################################

## Updated 2025. Written by Dave Prowse: https://prowse.tech

## This script will install the Prometheus Apache Exporter and run it as a service.

## It is tested on AMD64 and ARM64 - Ubuntu 22.04/24.04 and Debian 12, but should work on other systemd-based Linux distros as well.

## Prerequisites: Apache2 must be installed and running with mod_status enabled.

## Check that your firewalls have port 9117 open.

## To install a newer version simply change the version number in the variables below.

## !!! THIS IS FOR EDUCATIONAL PURPOSES ONLY. ONLY RUN THIS SCRIPT ON A TEST SYSTEM !!!

#########################################

# Variables
APACHE_EXPORTER_VERSION=v1.0.12
APACHE_EXPORTER_AMD64=apache_exporter-1.0.12.linux-amd64
APACHE_EXPORTER_ARM64=apache_exporter-1.0.12.linux-arm64

# sudo check and confirmation
clear -x
if [ "$(id -u)" -ne 0 ]; then echo;echo "Please run as root or with 'sudo'." >&2; echo; exit 1; fi

printf "\n\033[7;31mTHIS SCRIPT WILL INSTALL THE PROMETHEUS APACHE EXPORTER %s AND RUN IT AS A SERVICE. \033[0m" "$APACHE_EXPORTER_VERSION"
printf '%.0s\n' {1..2}
read -p "Are you sure you want to proceed? (y,n): " -r response
printf '%.0s\n' {1..2}
if [[ $response =~ ^[Yy]$ ]]; then
start=$SECONDS
printf '%.0s\n' {1..2}

sleep 1
mkdir temp
cd temp || return

# Determine CPU architecture
arch=$(uname -m)

# Download, extract, and copy Apache Exporter files
if [ "$arch" == "x86_64" ]; then
    echo "Installing package for x86_64 architecture..."
    wget https://github.com/Lusitaniae/apache_exporter/releases/download/$APACHE_EXPORTER_VERSION/$APACHE_EXPORTER_AMD64.tar.gz
    tar -xvf $APACHE_EXPORTER_AMD64.tar.gz
    cp ./$APACHE_EXPORTER_AMD64/apache_exporter /usr/local/bin
elif [ "$arch" == "aarch64" ]; then
    echo "Installing package for ARM64 architecture..."
    wget https://github.com/Lusitaniae/apache_exporter/releases/download/$APACHE_EXPORTER_VERSION/$APACHE_EXPORTER_ARM64.tar.gz
    tar -xvf $APACHE_EXPORTER_ARM64.tar.gz
    cp ./$APACHE_EXPORTER_ARM64/apache_exporter /usr/local/bin
else
    echo "Unsupported architecture: $arch"
    printf "Go to https://github.com/Lusitaniae/apache_exporter/releases to download other binaries."
    printf '%.0s\n' {1..2}
    exit 1
fi

# Set permissions
chmod +x /usr/local/bin/apache_exporter

# Create user
useradd -rs /bin/false apache_exporter 2>/dev/null || true

# Build apache_exporter service
cat << "EOF" > "/lib/systemd/system/apache_exporter.service"
[Unit]
Description=Apache Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=apache_exporter
Group=apache_exporter
Type=simple
ExecReload=/bin/kill -HUP $MAINPID
ExecStart=/usr/local/bin/apache_exporter \
  --scrape_uri=http://localhost/server-status?auto \
  --telemetry.endpoint=/metrics
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start apache_exporter service
systemctl daemon-reload
systemctl --now enable apache_exporter

# Clean UP!
cd .. || return
rm -rf temp/
sleep 2

# Completion messages
printf '%.0s\n' {1..2}
printf "\nTime to complete = %s seconds" "$SECONDS"
echo
apache_exporter --version 2>&1 | head -1
printf "\n\033[7;32mPROCESS COMPLETE! APACHE EXPORTER SHOULD NOW BE RUNNING AS A SERVICE AND LISTENING ON PORT 9117.\033[0m"
printf '%.0s\n' {1..2}
echo -e "Note: Make sure Apache mod_status is enabled. See the lab document for details."
printf '%.0s\n' {1..2}
printf "\n\033[7;36m ENJOY! \033[0m"
printf '%.0s\n' {1..2}

fi
