# Serverless Infrastructure Provisioning & Security Audit Pipeline

End-to-end Cloud Platform Engineering pipeline w/ scalable, serverless microservice architecture deployed via Terraform
Automated asset validation written in Python

*   **Serverless Infrastructure:** Provision decoupling application routers using AWS Lambda and HTTP API Gateway.
*   **Information Security:** Enforce scoped IAM policies based on the principle of least privilege.
*   **Automation Compliance:** Leverage Python and `boto3` to audit real-time deployment targets and infrastructure metadata.

*   **Cloud Platform:** Amazon Web Services (AWS API Gateway, AWS Lambda, IAM)
*   **IaC Engine:** Terraform (v1.0.0+)
*   **Language & SDK:** Python 3.x / Boto3 Core Library
*   **AI Accelerators:** GitHub Copilot / Claude 3.5 Sonnet
1.  **HCL Architecture Boilerplate:** Generated foundational API Gateway structural layout blocks to reduce baseline framework composition overhead.
2.  **Resource Mapping Optimization:** Used interactive prompts to configure context parameters for clean decoupling mapping inside the Lambda file asset execution paths.
3.  **Exception Mitigation:** Implemented robust schema processing handling to protect cross-functional runtime workflows against unmapped API metadata blocks.

Deployment Instructions

### 1. Provision Cloud Infrastructure
Ensure your AWS CLI profile is configured (`aws configure`). Initialize and execute the serverless deployment:
```bash
terraform init
terraform plan
terraform apply --auto-approve
```

### 2. Run the Compliance Audit
Trigger the compliance analyzer engine script:
```bash
pip install boto3
python audit_api.py
```
