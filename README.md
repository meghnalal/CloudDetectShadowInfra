# Terraform Drift Detection

A beginner-friendly walkthrough of Terraform drift: what it is, why it happens, and how to detect it using Python.

This repo contains the companion code for the full article — covering deploying resources through Terraform, simulating drift via ClickOps, and comparing the difference in Python.

📖 **Read the full article:** [Stop Terraform Drift Before It Stops You](https://medium.com/p/0b4ce33a3ba0)

## What's in this repo

- Terraform configuration to provision sample AWS resources
- A Python drift detection script that compares live AWS state against Terraform state
- Example output showing coverage percentage and "dark" (untracked) resources

## Getting started

Clone the repo and follow along with the article to deploy your own test resources, or swap in your own infrastructure.

```bash
git clone <this-repo-url>
```

## License

MIT
