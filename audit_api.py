"""
Standalone audit CLI for local testing and CI/CD.
Runs the same audit engine as Lambda but offline.
"""

import json
import sys
from lambda_function import ComplianceAudit


def print_audit_report(audit_results: dict) -> None:
    """Print formatted audit results."""
    print("\n" + "="*80)
    print("AWS INFRASTRUCTURE COMPLIANCE AUDIT REPORT")
    print("="*80)
    
    print(f"\nAudit Timestamp: {audit_results['timestamp']}")
    print(f"Total Resources Audited: {audit_results['total_resources_audited']}")
    print(f"Compliant Resources: {audit_results['compliant_resources']}")
    print(f"Non-Compliant Resources: {audit_results['non_compliant_resources']}")
    print(f"Compliance Percentage: {audit_results['compliance_percentage']}%")
    
    print("\n" + "-"*80)
    print("DETAILED FINDINGS")
    print("-"*80)
    
    # Group results by resource type
    by_type = {}
    for result in audit_results['audit_results']:
        resource_type = result.get('resource_type', 'UNKNOWN')
        if resource_type not in by_type:
            by_type[resource_type] = []
        by_type[resource_type].append(result)
    
    for resource_type, resources in by_type.items():
        print(f"\n{resource_type}:")
        for resource in resources:
            if resource.get('status') == 'ERROR':
                print(f"  ✗ ERROR: {resource.get('error', 'Unknown error')}")
            else:
                status = "✓ PASS" if resource.get('compliant', False) else "✗ FAIL"
                resource_id = resource.get('resource_id', resource.get('resource_name', 'N/A'))
                print(f"  {status} - {resource_id}")
                
                findings = resource.get('findings', {})
                for finding_key, finding_value in findings.items():
                    print(f"      • {finding_key}: {finding_value}")
    
    print("\n" + "="*80)


def save_audit_report(audit_results: dict, filename: str = 'audit_report.json') -> None:
    """Save results to JSON."""
    with open(filename, 'w') as f:
        json.dump(audit_results, f, indent=2)
    print(f"\nAudit report saved to: {filename}")


def main():
    """Run audit, print results, save report."""
    print("Starting AWS Infrastructure Compliance Audit...")
    
    try:
        audit_engine = ComplianceAudit()
        audit_results = audit_engine.run_audit()
        
        # Print report
        print_audit_report(audit_results)
        
        # Save report
        save_audit_report(audit_results)
        
        # Exit with appropriate code
        if audit_results['non_compliant_resources'] > 0:
            print(f"\n⚠️  Found {audit_results['non_compliant_resources']} non-compliant resource(s)")
            sys.exit(1)
        else:
            print("\n✓ All resources are compliant!")
            sys.exit(0)
    
    except Exception as e:
        print(f"\n✗ Audit failed with error: {str(e)}", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
