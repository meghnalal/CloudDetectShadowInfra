
import sys
import boto3
from botocore.exceptions import NoCredentialsError
from dataclasses import dataclass, field, asdict
from rich.console import Console
from constant import SKIP_RESOURCE_TYPES, RESOURCE_TYPE_MAP, SKIP_RESOURCE_TYPES, SEVERITY, SEVERITY_ORDER, SEVERITY_COLOURS

console = Console()

# schema for DarkResources
@dataclass
class DarkResource:
    arn: str
    resource_type: str
    resource_id: str
    region: str
    service: str
    severity: str
    managed_by_tag: str | None = None
   
# schema for ShadowInfraReport  
@dataclass
class ShadowInfraReport:
    """The output of a full drift scan."""
    account_id: str
    total_cloud: int = 0
    total_managed: int = 0
    dark_resources: list = field(default_factory=list)
    unmapped_types: dict[str, int] = field(default_factory=dict)

    @property
    def dark_count(self) -> int:
        return len(self.dark_resources)

    @property
    def coverage_pct(self) -> float:
        if self.total_cloud == 0:
            return 100.0
        return (self.total_cloud - self.dark_count) / self.total_cloud * 100

class Comparison: 
    
    def __init__(self,scanner,tfstate):
        # initialise aws
        self.account_id    = self._verify_credentials()
        self.home_region   = "eu-west-2"
        self.scanner = scanner
        self.tfstate = tfstate
        self.comparison     = self.compare(self.scanner,self.tfstate)
                
    def _verify_credentials(self) -> str:
        try:
            identity = boto3.client("sts").get_caller_identity()
            console.log(f"AWS identity confirmed: [cyan]{identity['Arn']}[/cyan]")
            return identity["Account"]
        except NoCredentialsError:
            console.print("[bold red]No AWS credentials found.[/bold red] Configure via environment, ~/.aws/credentials, or IAM role.")
            sys.exit(1)
                
    def compare(
        self,
        cloud_inventory: dict[str, list[dict]],
        tf_resources: dict[str, set[str]],
    ) -> ShadowInfraReport:

        report = ShadowInfraReport(account_id=self.account_id)
        dark: list = []

        for aws_type, resources in cloud_inventory.items():
            tf_type = RESOURCE_TYPE_MAP.get(aws_type)

            if not tf_type:
                # Type not in our map — count it but can't compare
                if aws_type not in SKIP_RESOURCE_TYPES:
                    report.unmapped_types[aws_type] = len(resources)
                continue

            managed_ids = tf_resources.get(tf_type, set())

            for r in resources:
                arn = r["arn"]
                rid = r["id"] or arn

                # Check both short ID and ARN — Terraform is inconsistent about which it stores
                if rid not in managed_ids and arn not in managed_ids:
                    parts   = arn.split(":")
                    service = parts[2] if len(parts) > 2 else aws_type.split(":")[0]
                    dark.append(DarkResource(
                            arn=arn,
                            resource_type=aws_type,
                            resource_id=rid,
                            region=r["region"],
                            service=service,
                            severity=SEVERITY.get(aws_type, "UNKNOWN"),
                            managed_by_tag=r.get("tags", {}).get("ManagedBy"),
                        )
                    )
                    

        # Sort by severity then type for consistent output
        dark.sort(key=lambda x: (SEVERITY_ORDER[x.severity], x.resource_type))
        # adding the whole dark resources in that 
        report.dark_resources = dark

        # Totals — count all trackable cloud resources
        report.total_cloud = sum(
            len(v) for k, v in cloud_inventory.items()
            if k not in SKIP_RESOURCE_TYPES
        )
        report.total_managed = sum(len(v) for v in tf_resources.values())
        
        return report

