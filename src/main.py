from cloudinventory import CloudInventory
from cloudstateinventory import CloudStateInventory
from comparison import Comparison
import json
from dataclasses import asdict

def main():
    print("\n=== Cloud Infrastructure Code ===")
    scanner = CloudInventory()
    # method name inventory
    cloud_inventory = scanner.inventory
    
    
    print("\n=== Cloud State Code ===")
    tfstate = CloudStateInventory("s3://driftdetectionstate/terraform.tfstate")
    # method name readstate
    tf_resources = tfstate.readstate
    
    print("\n=== Comparison ===")
    comparison = Comparison(cloud_inventory, tf_resources)
    comp = comparison.comparison 
    
    print(f"Coverage: {comp.coverage_pct:.1f}%")
    print(f"Dark resources found: {comp.dark_count}")
    for d in comp.dark_resources:
        print(f"  [{d.severity}] {d.resource_type} — {d.arn}")
    print(len(comp.dark_resources))
    
    report_dark_resources = {
        "coverage_pct": round(comp.coverage_pct, 1),
        "dark_count": comp.dark_count,
        "dark_resources": [
            {
                "severity": d.severity,
                "resource_type": d.resource_type,
                "arn": d.arn,
            }
            for d in comp.dark_resources
        ],
    }
    
    with open("report_dark_resources.json", "w") as f:
        json.dump(report_dark_resources, f, indent=2, default=str)
    
    return comp


if __name__ == "__main__":
    main()