SKIP_RESOURCE_TYPES = {
    "ec2:dhcp-options",           # auto-created with every VPC
    "ec2:network-acl",            # auto-created with every VPC
    "ec2:network-interface",      # auto-created by instances/ENIs
    "iam:instance-profile",       # auto-created alongside IAM roles
    "ec2:flow-log",               # auto-created by security tooling
    "lambda:function/version",    # auto-created on every Lambda deploy
    "resource-explorer-2:index",  # the scanner tool itself
    "resource-explorer-2:view",   # the scanner tool itself
}

RESOURCE_TYPE_MAP = {
    # ── EC2 ───────────────────────────────────────────────────────────────────
    "ec2:instance":                                  "aws_instance",
    "ec2:security-group":                            "aws_security_group",
    "ec2:security-group-rule":                       "aws_vpc_security_group_ingress_rule",
    "ec2:subnet":                                    "aws_subnet",
    "ec2:vpc":                                       "aws_vpc",
    "ec2:internet-gateway":                          "aws_internet_gateway",
    "ec2:route-table":                               "aws_route_table",
    "ec2:volume":                                    "aws_ebs_volume",
    "ec2:elastic-ip":                                "aws_eip",
    "ec2:natgateway":                                "aws_nat_gateway",
    "ec2:key-pair":                                  "aws_key_pair",
    "ec2:network-interface":                         "aws_network_interface",
    # ── S3 ───────────────────────────────────────────────────────────────────
    "s3:bucket":                                     "aws_s3_bucket",
    # ── Lambda ───────────────────────────────────────────────────────────────
    "lambda:function":                               "aws_lambda_function",
    # ── RDS ──────────────────────────────────────────────────────────────────
    "rds:db":                                        "aws_db_instance",
    "rds:cluster":                                   "aws_rds_cluster",
    # ── IAM ──────────────────────────────────────────────────────────────────
    "iam:role":                                      "aws_iam_role",
    "iam:policy":                                    "aws_iam_policy",
    "iam:user":                                      "aws_iam_user",
    "iam:group":                                     "aws_iam_group",
    # ── KMS ──────────────────────────────────────────────────────────────────
    "kms:key":                                       "aws_kms_key",
    # ── SQS / SNS ────────────────────────────────────────────────────────────
    "sqs:queue":                                     "aws_sqs_queue",
    "sns:topic":                                     "aws_sns_topic",
    # ── EKS / ECS ────────────────────────────────────────────────────────────
    "eks:cluster":                                   "aws_eks_cluster",
    "eks:nodegroup":                                 "aws_eks_node_group",
    "ecs:cluster":                                   "aws_ecs_cluster",
    "ecs:service":                                   "aws_ecs_service",
    # ── Load Balancers ────────────────────────────────────────────────────────
    "elasticloadbalancing:loadbalancer/application": "aws_lb",
    "elasticloadbalancing:loadbalancer/network":     "aws_lb",
    "elasticloadbalancing:targetgroup":              "aws_lb_target_group",
    # ── CloudFront ───────────────────────────────────────────────────────────
    "cloudfront:distribution":                       "aws_cloudfront_distribution",
    # ── DynamoDB ─────────────────────────────────────────────────────────────
    "dynamodb:table":                                "aws_dynamodb_table",
    # ── ElastiCache / MemoryDB ───────────────────────────────────────────────
    "elasticache:cluster":                           "aws_elasticache_cluster",
    "elasticache:replicationgroup":                  "aws_elasticache_replication_group",
    "elasticache:user":                              "aws_elasticache_user",
    "memorydb:cluster":                              "aws_memorydb_cluster",
    "memorydb:acl":                                  "aws_memorydb_acl",
    "memorydb:user":                                 "aws_memorydb_user",
    "memorydb:parametergroup":                       "aws_memorydb_parameter_group",
    # ── Secrets / SSM ────────────────────────────────────────────────────────
    "secretsmanager:secret":                         "aws_secretsmanager_secret",
    "ssm:parameter":                                 "aws_ssm_parameter",
    # ── CloudWatch / Logs / Events ───────────────────────────────────────────
    "cloudwatch:alarm":                              "aws_cloudwatch_metric_alarm",
    "logs:log-group":                                "aws_cloudwatch_log_group",
    "events:rule":                                   "aws_cloudwatch_event_rule",
    "events:event-bus":                              "aws_cloudwatch_event_bus",
    # ── Route53 ──────────────────────────────────────────────────────────────
    "route53:hostedzone":                            "aws_route53_zone",
    # ── Cognito ──────────────────────────────────────────────────────────────
    "cognito-idp:userpool":                          "aws_cognito_user_pool",
    # ── SES ──────────────────────────────────────────────────────────────────
    "ses:identity":                                  "aws_ses_domain_identity",
    # ── Athena ───────────────────────────────────────────────────────────────
    "athena:workgroup":                              "aws_athena_workgroup",
    "athena:datacatalog":                            "aws_glue_catalog_database",
    # ── App Runner ───────────────────────────────────────────────────────────
    "apprunner:service":                             "aws_apprunner_service",
    "apprunner:autoscalingconfiguration":            "aws_apprunner_auto_scaling_configuration_version",
    # ── AutoScaling ──────────────────────────────────────────────────────────
    "autoscaling:autoScalingGroup":                  "aws_autoscaling_group",
    # ── X-Ray ────────────────────────────────────────────────────────────────
    "xray:sampling-rule":                            "aws_xray_sampling_rule",
}

# Resource types to skip — AWS-managed, auto-created, or too noisy to track
SKIP_RESOURCE_TYPES = {
    "ec2:dhcp-options",           # auto-created with every VPC
    "ec2:network-acl",            # auto-created with every VPC
    "ec2:network-interface",      # auto-created by instances/ENIs
    "iam:instance-profile",       # auto-created alongside IAM roles
    "ec2:flow-log",               # auto-created by security tooling
    "lambda:function/version",    # auto-created on every Lambda deploy
    "resource-explorer-2:index",  # the scanner tool itself
    "resource-explorer-2:view",   # the scanner tool itself
}

SEVERITY = {
    # CRITICAL — identity, access, encryption
    "iam:role":                        "CRITICAL",
    "iam:policy":                      "CRITICAL",
    "iam:user":                        "CRITICAL",
    "kms:key":                         "CRITICAL",
    "secretsmanager:secret":           "CRITICAL",
    # HIGH — compute, data, networking perimeter
    "ec2:instance":                    "HIGH",
    "ec2:security-group":              "HIGH",
    "s3:bucket":                       "HIGH",
    "rds:db":                          "HIGH",
    "rds:cluster":                     "HIGH",
    "eks:cluster":                     "HIGH",
    "cognito-idp:userpool":            "HIGH",
    "ses:identity":                    "HIGH",
    # MEDIUM — application layer
    "lambda:function":                 "MEDIUM",
    "ecs:service":                     "MEDIUM",
    "elasticloadbalancing:loadbalancer/application": "MEDIUM",
    "elasticloadbalancing:loadbalancer/network":     "MEDIUM",
    "ec2:vpc":                         "MEDIUM",
    "events:rule":                     "MEDIUM",
    "events:event-bus":                "MEDIUM",
    # LOW — supporting resources
    "ec2:subnet":                      "LOW",
    "sqs:queue":                       "LOW",
    "sns:topic":                       "LOW",
    "logs:log-group":                  "LOW",
    "cloudwatch:alarm":                "LOW",
    "xray:sampling-rule":              "LOW",
    "athena:workgroup":                "LOW",
    "memorydb:acl":                    "LOW",
    "memorydb:user":                   "LOW",
    "memorydb:parametergroup":         "LOW",
}

SEVERITY_ORDER  = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}

SEVERITY_COLOURS = {
    "CRITICAL": "bold red",
    "HIGH":     "red",
    "MEDIUM":   "yellow",
    "LOW":      "cyan",
    "UNKNOWN":  "white",
}
