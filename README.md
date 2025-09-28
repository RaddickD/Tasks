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
Run using Docker:

bash
Copy code
docker run --rm -v $(pwd)/config.yaml:/app/config.yaml cert-checker
Or run using Docker Compose:

bash
Copy code
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

Usage
Initialize Terraform:

bash
Copy code
cd TASK2/azure-infrastructure/terraform
terraform init
Validate configuration:

bash
Copy code
terraform validate
Plan deployment:

bash
Copy code
terraform plan
Apply deployment:

bash
Copy code
terraform apply
Note: Ensure that Azure credentials are correctly configured. You may use environment variables or a service principal.

Repository Directory Tree
arduino
Copy code
.
├── TASK1
│   └── cert-checker
│       ├── Dockerfile
│       ├── README.md
│       ├── cert_checker.py
│       ├── config.yaml
│       ├── docker-compose.yml
│       └── requirements.txt
└── TASK2
    └── azure-infrastructure
        ├── scripts
        └── terraform
            ├── main.tf
            ├── outputs.tf
            ├── provider.tf
            └── variables.tf
Notes
Ensure Docker and Terraform are installed for the respective tasks.

Update configuration files (config.yaml for TASK1, variables.tf for TASK2) before running.

This README provides a complete overview for both tasks and can serve as a quick reference.
