# Shadow Infrastructure Detection

A beginner-friendly walkthrough of shadow infrastructure: what it is, why it happens, and how to detect it using Python.

This repo contains the companion code for the full article, covering deploying resources through Terraform, simulating shadow infrastructure via ClickOps, and comparing the difference in Python.

📖 **Read the full article:** [The Terraform Blind Spot Nobody Talks About](https://medium.com/aws-in-plain-english/the-terraform-blind-spot-nobody-talks-about-0b4ce33a3ba0)

## What's in this repo

- Terraform configuration to provision sample AWS resources
- A Python script that detects shadow infrastructure by comparing live AWS state against Terraform state
- Example output showing coverage percentage and "dark" (unmanaged) resources

## Getting started

Clone the repo and follow along with the article to deploy your own test resources, or swap in your own infrastructure.

```bash
git clone git@github.com:meghnalal/CloudDetectShadowInfra.git
```

## License

MIT