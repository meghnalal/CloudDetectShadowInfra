import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dataclasses import dataclass, field, asdict
from rich.console import Console
from constant import SKIP_RESOURCE_TYPES


console = Console()

class CloudInventory:
    def __init__(self):
        # initialise aws
        self.account_id    = self._verify_credentials()
        self.home_region   = "eu-west-2"
        self.inventory     = self.collect()

    def _verify_credentials(self) -> str:
        try:
            identity = boto3.client("sts").get_caller_identity()
            console.log(f"AWS identity confirmed: [cyan]{identity['Arn']}[/cyan]")
            return identity["Account"]
        except NoCredentialsError:
            console.print("[bold red]No AWS credentials found.[/bold red] Configure via environment, ~/.aws/credentials, or IAM role.")
            sys.exit(1)
            
    def collect(self) -> dict[str, list[dict]]:
        console.log("Querying AWS Resource Explorer...")
        regions = self._get_index_regions()
        
        inventory: dict[str, list[dict]] = {}
        for region in regions:
            console.log(f"  Scanning region: [cyan]{region}[/cyan]")
            regional = self._query_region(region)
    
            for rtype, resources in regional.items():
                inventory.setdefault(rtype, []).extend(resources)
    
        total = sum(len(v) for v in inventory.values())
        console.log(f"Found [bold]{total}[/bold] resources across [bold]{len(inventory)}[/bold] resource types")
        console.log(f"Found [bold]{total}[/bold] resources across [bold]{(inventory)}[/bold] resource types")
    
        return inventory        
                
    # need to use resource-explorer-2 api but also to be able to use it need to upgrade 
    def _get_index_regions(self) -> list[str]:
        """Find which regions have Resource Explorer 
            indexes and pick the right ones to query."""
            
        client = boto3.client("resource-explorer-2", region_name=self.home_region)
        try:
            indexes = client.list_indexes().get("Indexes", [])
        except ClientError as e:
            console.print(f"[bold red]Error listing Resource Explorer indexes:[/bold red] {e}")
            sys.exit(1)

        # if there is not any index [potentially issue on gitlab-runner? job to install boto3 and add index]
        if not indexes:
            console.print(
                "[bold red]No Resource Explorer indexes found.[/bold red]\n"
                "Promote an existing local index to AGGREGATOR:\n"
                "[cyan]aws resource-explorer-2 update-index-type "
                "--arn <your-in dex-arn> --type AGGREGATOR --region eu-west-2[/cyan]"
            )
            sys.exit(1)

        aggregators = [i for i in indexes if i.get("Type") == "AGGREGATOR"]
        if aggregators:
            console.log(f"Found AGGREGATOR index in [cyan]{aggregators[0]['Region']}[/cyan] — single query covers all regions")
            return [aggregators[0]["Region"]]

        # Fall back to querying each local index separately if no aggregator found 
        regions = [i["Region"] for i in indexes if i.get("Type") == "LOCAL"]
        console.log(
            f"[yellow]No AGGREGATOR found. Querying {len(regions)} LOCAL indexes: {regions}[/yellow]\n"
            f"[dim]Tip: promote one to AGGREGATOR for full single-query coverage[/dim]"
        )
        return regions
            
    def _query_region(self, region: str) -> dict[str, list[dict]]:
        """Query a single Resource Explorer index and return its resources."""
        client = boto3.client("resource-explorer-2", region_name=region)
        inventory: dict[str, list[dict]] = {}
        next_token = None

        while True:
            # you need to add a queystring parrameter - not optional
            #  empty string == no filter 
            
            
            # if next_token:
            #     response = client.search(QueryString="", NextToken=next_token)
            # else:
            #     response = client.search(QueryString="")

            kwargs: dict = {"QueryString": ""}  # empty = return everything
            # if there's a next page token...
            if next_token:
                # ...add it to the request to get the next page
                kwargs["NextToken"] = next_token

            try:
                # this what actually list all my resources with ""
                # kwargs: dict = {"QueryString": ""}
                # kwargs: dict = {"QueryString": "", "NextToken": next_token}}, 
                response = client.search(**kwargs)
            except ClientError as e:
                if e.response["Error"]["Code"] == "AccessDeniedException":
                    console.print(f"[red]Access denied querying Resource Explorer in {region}[/red]")
                    break
                raise
            
            # {Resources: [ {arn:... ResourceType:...}, {arn:... ResourceType:...} ] }
            for resource in response.get("Resources", []):
                # extracting resourceType or unknown ones
                rtype = resource.get("ResourceType", "UNKNOWN").lower()
                if rtype in SKIP_RESOURCE_TYPES:
                    continue

                # Flatten tags from the Properties array
                # Extracting tags if there is any
                tags = {}
                for prop in resource.get("Properties", []):
                    if prop.get("Name") == "tags":
                        # loop through each tag
                        for tag in prop.get("Data", []):
                            if isinstance(tag, dict) and "Key" in tag:
                                 # add to our tags dict e.g. tags["Environment"] = "prod"
                                 # if no Value exists, default to empty string ""
                                tags[tag["Key"]] = tag.get("Value", "")

                inventory.setdefault(rtype, []).append({
                    "arn":    resource.get("Arn", ""),
                    "id":     resource.get("Id", ""),
                    "region": resource.get("Region", region),
                    "tags":   tags,
                })

            next_token = response.get("NextToken")
            if not next_token:
                break

        return inventory
            
        
        
        
    