# Project Repository

This repository contains multiple tasks, including a certificate checker and an Azure infrastructure setup using Terraform.

---

## TASK1: Certificate Checker

**Location:** `TASK1/cert-checker`

This task provides a Python-based tool to check SSL/TLS certificates. It is containerized using Docker and can be orchestrated with Docker Compose.

### Files:

- `Dockerfile` — Docker image definition for the certificate checker.
- `README.md` — Documentation for TASK1.
- `cert_checker.py` — Python script for checking certificates.
- `config.yaml` — Configuration file with target domains and options.
- `docker-compose.yml` — Docker Compose setup for running the container.
- `requirements.txt` — Python dependencies.

### Usage

1. Build the Docker image:

```bash
docker build -t cert-checker .
docker run --rm -v $(pwd)/config.yaml:/app/config.yaml cert-checker
docker-compose up


## TASK2: Azure Infrastructure

Location: TASK2/azure-infrastructure

This task sets up Azure infrastructure using Terraform. The configuration provisions resources in Azure based on the variables defined.

Folder Structure

scripts/ — Contains helper scripts for deployment or configuration.

terraform/ — Contains Terraform configuration files.

Terraform Files

main.tf — Main Terraform configuration defining resources.

outputs.tf — Outputs of the Terraform deployment.

provider.tf — Azure provider setup (subscription, credentials).

variables.tf — Input variables for the infrastructure.
