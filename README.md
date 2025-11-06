# Prometheus Video Course Labs

Copyright © Dave Prowse

Website: https://prowse.tech

Discord Server: https://discord.gg/mggw8VGzUp

---

This is the repository for the following Prometheus video courses:

- Prometheus Certified Associate (PCA)
- Prometheus Fundamentals

All of the labs can be found within.

Link: https://github.com/daveprowse/prom-course

## Prepare Linux VMs!

Although you can get away with a single Linux system for this course, I highly recommend that you prepare at least two, local, Linux virtual machines in a NAT network. One to run Prometheus, and the other to be monitored. This is a best practice that will allow your systems to be somewhat isolated from your main system and network. Make sure that your main system can communicate with the virtual machines via SSH and web browser.

The scripts and labs are designed for **Ubuntu** Server or **Debian** server (x64 platform). Work as root or as a user with sudo powers.

If you don't have either Ubuntu or Debian you can download them from the following links.

- Ubuntu Server [Download](https://ubuntu.com/download/server)
- Debian [Download](https://www.debian.org/download)

> Note: If you choose to run Debian, make sure that you install it as a server. To do so, deselect any desktops (GNOME, KDE, etc...) during the Task Selection phase of the installation.

Most importantly, to install Prometheus see the first lab at [this link](./labs/lab-01/README.md).

> Note: I don't recommend WSL or cloud-based systems. Instead, run your virtual machines locally with a tool such as VirtualBox, VMware Workstation, or Proxmox. This will provide you with the best results.

> Note: If you are unsure how to set up a proper NAT network in VirtualBox, see [this link](https://prowse.tech/virtualbox/)

## Kubernetes

You might also be interested in running, and monitoring, Kubernetes. Here are a few options. For this video course, I recommend, and  will be monitoring a MicroK8s cluster.

- **MicroK8s Cluster** (three Ubuntu virtual machines). This is my main setup for this course. It's quite easy to install. For more information click [here](./z-more-info/microk8s/microk8s-notes.md).

You could also set up Kubernetes with one of the following options:

- **MiniKube**: For details on how to setup a Minkube, click [here](./z-more-info/minikube/minikube-install.md). If you want to run minikube then I recommend doing it on a Linux system with a GUI (desktop interface).

- **Vanilla Kubernetes cluster** (three Ubuntu virtual machines). For scripts and details for installing an actual Kubernetes cluster, click [here](./z-more-info/k8s-scripts/README.md).

---

## Docker

You could run everything for this course on a single VM running Docker.

**Docker Installation [Link](https://docs.docker.com/engine/install/)**

You could get away with using Docker for everything: A Prometheus docker image, a Docker-based MiniKube, and a separate Debian Docker image to be monitored, and the whole thing could run on a single system and be fairly lightweight. The downside is that you will lose some functionality and won't be able to follow along with everything we cover in the course. But it's a good substitute if you can't run several virtual machines and/or full K8s clusters.

## Dave's Lab and Suggestions

For the video course I will be using two Ubuntu servers, a Debian client running minikube, and a MicroK8s cluster with a controller and two workers. Here's what you will need:

- For the Prometheus Fundamentals Video Course: Only two Ubuntu servers.
- For the Prometheus PCA Video Course: Two Ubuntu servers and some kind of K8s cluster (MicroK8s is recommended).

---

**🌞 I hope you enjoy the course!**

---
