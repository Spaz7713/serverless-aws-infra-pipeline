<<<<<<< HEAD
# AWS Infrastructure Compliance Audit

Serverless audit pipeline that checks AWS resources against compliance rules. Runs on Lambda, triggered via API Gateway, provisions with OpenTofu.

## What It Does

- Scans IAM policies for wildcard permissions
- Checks S3 buckets for encryption & public access
- Finds overly permissive security groups
- Returns results as JSON via REST API or CLI

## Stack

- **API**: API Gateway HTTP API
- **Compute**: AWS Lambda (Python 3.11)
- **IaC**: OpenTofu
- **SDK**: boto3

## Quick Start

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Create Lambda zip
zip lambda_function.zip lambda_function.py

# 3. Deploy
tofu init
tofu apply -var="environment=dev"

# 4. Get URL
tofu output audit_url
```

## Usage

**Via API:**
```bash
curl https://<api-endpoint>/dev/audit

# Specific audit types
curl "https://<api-endpoint>/dev/audit?type=iam"
curl "https://<api-endpoint>/dev/audit?type=s3"
curl "https://<api-endpoint>/dev/audit?type=security_groups"
```

**Locally:**
```bash
python audit_api.py
# Generates audit_report.json
```

## What Gets Checked

**IAM** - Wildcard permissions, least privilege violations

**S3** - Encryption enabled, public access blocked

**Security Groups** - No 0.0.0.0/0 access

## Output

```json
{
  "timestamp": "2024-06-19T12:34:56.789123",
  "total_resources_audited": 15,
  "compliant_resources": 12,
  "non_compliant_resources": 3,
  "compliance_percentage": 80.0,
  "audit_results": [...]
}
```

## Customize

```bash
tofu apply -var="environment=prod" \
           -var="aws_region=us-west-2" \
           -var="project_name=my-audit"
```

## Teardown

```bash
tofu destroy --auto-approve
```

## Notes

- Lambda role is read-only (least privilege)
- Logs retained 7 days
- 60s timeout, 512MB memory
=======
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
>>>>>>> 0ce3117a029833e5eb06afe903f65fb229974602
