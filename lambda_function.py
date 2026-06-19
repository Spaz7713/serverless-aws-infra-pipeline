<<<<<<< HEAD
"""
Compliance audit engine for AWS resources.
Triggered by API Gateway, runs audit checks against IAM, S3, and Security Groups.
"""

import json
import logging
from typing import Dict, List, Any
import boto3
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
iam_client = boto3.client('iam')
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')
kms_client = boto3.client('kms')


class ComplianceAudit:
    """Main audit engine - runs all compliance checks."""
    
    def __init__(self):
        self.audit_results = []
        self.audit_timestamp = datetime.utcnow().isoformat()
    
    def audit_iam_policies(self) -> List[Dict[str, Any]]:
        """Check IAM policies for wildcard permissions (least privilege violations)."""
        results = []
        try:
            # Get all IAM users
            users = iam_client.list_users()['Users']
            
            for user in users:
                user_name = user['UserName']
                
                # Check for inline policies
                inline_policies = iam_client.list_user_policies(UserName=user_name)['PolicyNames']
                
                for policy_name in inline_policies:
                    policy_doc = iam_client.get_user_policy(
                        UserName=user_name,
                        PolicyName=policy_name
                    )['PolicyDocument']
                    
                    # Check for wildcards (*) in actions or resources (least privilege violations)
                    has_wildcard_action = self._check_wildcard_actions(policy_doc)
                    has_wildcard_resource = self._check_wildcard_resources(policy_doc)
                    
                    results.append({
                        'resource_type': 'IAM_USER_INLINE_POLICY',
                        'resource_id': f"{user_name}/{policy_name}",
                        'compliant': not (has_wildcard_action or has_wildcard_resource),
                        'findings': {
                            'wildcard_actions': has_wildcard_action,
                            'wildcard_resources': has_wildcard_resource
                        }
                    })
            
            logger.info(f"IAM Policy audit completed: {len(results)} policies checked")
        except Exception as e:
            logger.error(f"Error auditing IAM policies: {str(e)}")
            results.append({
                'resource_type': 'IAM_AUDIT',
                'status': 'ERROR',
                'error': str(e)
            })
        
        return results
    
    def audit_s3_buckets(self) -> List[Dict[str, Any]]:
        """Check S3 buckets for encryption and public access blocks."""
        results = []
        try:
            buckets = s3_client.list_buckets()['Buckets']
            
            for bucket in buckets:
                bucket_name = bucket['Name']
                
                # Check encryption
                try:
                    encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
                    has_encryption = True
                except s3_client.exceptions.ServerSideEncryptionConfigurationNotFoundError:
                    has_encryption = False
                
                # Check public access block
                try:
                    public_access = s3_client.get_public_access_block(Bucket=bucket_name)
                    block_settings = public_access['PublicAccessBlockConfiguration']
                    is_blocked = all([
                        block_settings.get('BlockPublicAcls', False),
                        block_settings.get('BlockPublicPolicy', False),
                        block_settings.get('IgnorePublicAcls', False),
                        block_settings.get('RestrictPublicBuckets', False)
                    ])
                except s3_client.exceptions.NoSuchPublicAccessBlockConfiguration:
                    is_blocked = False
                
                results.append({
                    'resource_type': 'S3_BUCKET',
                    'resource_id': bucket_name,
                    'compliant': has_encryption and is_blocked,
                    'findings': {
                        'encryption_enabled': has_encryption,
                        'public_access_blocked': is_blocked
                    }
                })
            
            logger.info(f"S3 bucket audit completed: {len(results)} buckets checked")
        except Exception as e:
            logger.error(f"Error auditing S3 buckets: {str(e)}")
            results.append({
                'resource_type': 'S3_AUDIT',
                'status': 'ERROR',
                'error': str(e)
            })
        
        return results
    
    def audit_security_groups(self) -> List[Dict[str, Any]]:
        """Check security groups for overly permissive inbound rules (0.0.0.0/0)."""
        results = []
        try:
            security_groups = ec2_client.describe_security_groups()['SecurityGroups']
            
            for sg in security_groups:
                sg_id = sg['GroupId']
                sg_name = sg['GroupName']
                
                has_overly_permissive = False
                
                # Check inbound rules for 0.0.0.0/0 access
                for rule in sg.get('IpPermissions', []):
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            has_overly_permissive = True
                            break
                
                results.append({
                    'resource_type': 'SECURITY_GROUP',
                    'resource_id': sg_id,
                    'resource_name': sg_name,
                    'compliant': not has_overly_permissive,
                    'findings': {
                        'overly_permissive_rules': has_overly_permissive
                    }
                })
            
            logger.info(f"Security group audit completed: {len(results)} groups checked")
        except Exception as e:
            logger.error(f"Error auditing security groups: {str(e)}")
            results.append({
                'resource_type': 'SECURITY_GROUP_AUDIT',
                'status': 'ERROR',
                'error': str(e)
            })
        
        return results
    
    def _check_wildcard_actions(self, policy_doc: Dict) -> bool:
        """Detect * in Action statements."""
        for statement in policy_doc.get('Statement', []):
            actions = statement.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]
            if '*' in actions or any('*' in action for action in actions):
                return True
        return False
    
    def _check_wildcard_resources(self, policy_doc: Dict) -> bool:
        """Detect * in Resource statements."""
        for statement in policy_doc.get('Statement', []):
            resources = statement.get('Resource', [])
            if isinstance(resources, str):
                resources = [resources]
            if '*' in resources or any(resource == '*' for resource in resources):
                return True
        return False
    
    def run_audit(self) -> Dict[str, Any]:
        """Run all three audit types and return summary."""
        logger.info("Starting compliance audit...")
        
        all_results = []
        all_results.extend(self.audit_iam_policies())
        all_results.extend(self.audit_s3_buckets())
        all_results.extend(self.audit_security_groups())
        
        compliant_count = sum(1 for r in all_results if r.get('compliant', False))
        non_compliant_count = sum(1 for r in all_results if r.get('compliant') == False)
        
        return {
            'timestamp': self.audit_timestamp,
            'total_resources_audited': len(all_results),
            'compliant_resources': compliant_count,
            'non_compliant_resources': non_compliant_count,
            'compliance_percentage': round(
                (compliant_count / len(all_results) * 100) if all_results else 0, 2
            ),
            'audit_results': all_results
        }


def lambda_handler(event, context):
    """API Gateway handler - runs audit and returns JSON response."""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract query parameters
        query_params = event.get('queryStringParameters') or {}
        audit_type = query_params.get('type', 'full')
        
        # Run compliance audit
        audit_engine = ComplianceAudit()
        
        if audit_type == 'iam':
            audit_results = {'results': audit_engine.audit_iam_policies()}
        elif audit_type == 's3':
            audit_results = {'results': audit_engine.audit_s3_buckets()}
        elif audit_type == 'security_groups':
            audit_results = {'results': audit_engine.audit_security_groups()}
        else:
            audit_results = audit_engine.run_audit()
        
        logger.info(f"Audit completed successfully")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(audit_results)
        }
    
    except Exception as e:
        logger.error(f"Error processing audit request: {str(e)}", exc_info=True)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Audit engine error',
                'message': str(e)
            })
        }
=======
>>>>>>> 0ce3117a029833e5eb06afe903f65fb229974602

