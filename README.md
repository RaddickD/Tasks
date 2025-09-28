# Tasks Repository

This repository contains DevOps tasks and automation scripts, including a certificate checker Dockerized application and Azure infrastructure scripts using Terraform.

## Project Structure

.
├── TASK1
│ └── cert-checker
│ ├── Dockerfile
│ ├── README.md
│ ├── cert_checker.py
│ ├── config.yaml
│ ├── docker-compose.yml
│ └── requirements.txt
└── TASK2
└── azure-infrastructure
├── scripts
└── terraform
├── main.tf
├── outputs.tf
├── provider.tf
└── variables.tf

bash
Copy code

## TASK1 – Certificate Checker

A Python-based application that checks SSL/TLS certificates, containerized with Docker.

### How to Run

**Using Docker Compose:**

```bash
cd TASK1/cert-checker
docker-compose up --build
Directly with Docker:

bash
Copy code
docker build -t cert-checker .
docker run -v $(pwd)/config.yaml:/app/config.yaml cert-checker
Python Environment (without Docker):

bash
Copy code
cd TASK1/cert-checker
pip install -r requirements.txt
python cert_checker.py --config config.yaml
TASK2 – Azure Infrastructure
Terraform scripts to provision Azure resources (virtual networks, storage, compute, etc.).

How to Run
bash
Copy code
cd TASK2/azure-infrastructure/terraform
terraform init
terraform plan
terraform apply
Notes
Log in to Azure CLI first:

bash
Copy code
az login
Use a .tfvars file or environment variables for secrets instead of committing them to Git.

Contributing
Contributions are welcome:

Fork the repository.

Create a feature branch:

bash
Copy code
git checkout -b feature-name
Make changes and commit:

bash
Copy code
git commit -m "Add new feature"
Push to your branch:

bash
Copy code
git push origin feature-name
Open a Pull Request for review.

License
This repository is licensed under the MIT License.

Contact
Created by Radoslav – DevOps Engineer.

For questions, open an issue in this repository.
