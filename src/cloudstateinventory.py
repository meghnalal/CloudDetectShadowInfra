import json
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dataclasses import dataclass, field, asdict
from rich.console import Console

console = Console()
class CloudStateInventory:

    def __init__(self, state_path: str):
        self.state_path = state_path
        self.readstate = self.read()

    def read(self) -> dict[str, set[str]]:
        """
        Returns a dict of Terraform resource type → set of IDs/ARNs.
        e.g. { "aws_s3_bucket": {"my-bucket", "other-bucket"} }
        """
        raw = self._load_file()
        resources = self._parse(raw)


        total = sum(len(v) for v in resources.values())
        console.log(f"Found [bold]{total}[/bold] resources in Terraform state across [bold]{len(resources)}[/bold] types")

        if total == 0:
            console.print(
                "[yellow]Warning: 0 resources found in state.[/yellow] "
                "The state may be empty (nothing applied yet) or the path is wrong."
            )
        print("resources",resources)
        return resources

    def _load_file(self) -> dict:
        """Load the raw state file from local path or S3."""
        if self.state_path.startswith("s3://"):
            return self._load_from_s3()
        return self._load_from_disk()

    def _load_from_s3(self) -> dict:
        parts  = self.state_path[5:].split("/", 1)
        bucket, key = parts[0], parts[1]
        console.log(f"Loading Terraform state from S3: [cyan]{self.state_path}[/cyan]")
        try:
            obj = boto3.client("s3").get_object(Bucket=bucket, Key=key)
            return json.loads(obj["Body"].read())
        except ClientError as e:
            console.print(f"[bold red]Failed to load state from S3:[/bold red] {e}")
            sys.exit(1)

    def _load_from_disk(self) -> dict:
        console.log(f"Loading Terraform state from local file: [cyan]{self.state_path}[/cyan]")
        try:
            with open(self.state_path) as f:
                return json.load(f)
        except FileNotFoundError:
            console.print(f"[bold red]State file not found:[/bold red] {self.state_path}")
            sys.exit(1)

    def _parse(self, state: dict) -> dict[str, set[str]]:
        """Auto-detect state format and extract resource IDs."""
        managed: dict[str, set[str]] = {}
        # There is 2 formats one the state and the other is the json 
        # {"resources": [{"type": "aws_s3_bucket", "mode": "managed", "instances": [{"attributes": {...}}]}]}
        
        # Format 1: Raw terraform.tfstate v4 — state.resources[]
        if state.get("resources"):
            console.log("Detected raw [cyan]terraform.tfstate[/cyan] format (v4)")
            # state[resources] loops through your resources list here 
            for resource in state["resources"]:
                if resource.get("mode") == "data":
                    continue   # skip data sources — they're read-only references
                rtype = resource.get("type", "")
                #  loops over instances because like a bucket could have multiple instances 
                for instance in resource.get("instances", []):
                    self._add_ids(managed, rtype, instance.get("attributes", {}))

        # Format 2: terraform show -json — state.values.root_module
        # state["values"]["root_module"]
        elif "values" in state:
            console.log("Detected [cyan]terraform show -json[/cyan] format")
            # walk module for recursion
            self._walk_module(managed, state["values"].get("root_module", {}))

        else:
            console.print("[bold red]Unrecognised state format.[/bold red] Expected terraform.tfstate v4 or terraform show -json.")
            sys.exit(1)

        return managed

    def _walk_module(self, managed: dict, module: dict):
        """Recursively walk root and child modules (handles nested module calls)."""
        for resource in module.get("resources", []):
            if resource.get("mode") == "data":
                continue
            self._add_ids(managed, resource.get("type", ""), resource.get("values", {}))
        for child in module.get("child_modules", []):
            self._walk_module(managed, child)

    def _add_ids(self, managed: dict, rtype: str, attrs: dict):
        """Extract all possible ID forms from a resource's attributes."""
        # tries sever field in priority order to extract info to identify it 
        rid = (
            attrs.get("id") or
            attrs.get("arn") or
            attrs.get("bucket") or   # S3 stores bucket name under "bucket" key
            attrs.get("name") or
            ""
        )
        if rid:
            managed.setdefault(rtype, set()).add(rid)
            # Also index ARN separately — Resource Explorer sometimes returns ARNs
            # where Terraform stored the short ID and vice versa
            arn = attrs.get("arn", "")
            if arn and arn != rid:
                managed.setdefault(rtype, set()).add(arn)
