# Backend Migration Plan: Render → AWS ECS Fargate

Scope: all tasks are within this repo (`resume-builder-backend`).  
Architecture context and deployment order live in [ARCHITECTURE.md](ARCHITECTURE.md).

CONSTRAINTS:
- no Git pushes, PRs ==> should be manual, hand off to human (i.e. stop executing) whenever you find yourself needing to do a Git Push or PR
- do not list yourself (Claude) as co-author
- commit messages should follow conventional commits
- every PR/feature should be a new branch


STAGES:
[TOVERIFY] - waiting for manual verification
[DONE] - tested & approved PR, ready to do next stage as outlined below

---

## PR 1 — Django Settings Cleanup [DONE]

**Goal:** Remove Render/Vercel dependencies from `settings.py` so the backend is environment-agnostic.

### Changes

**File: `resume-builder-django/core/settings.py`**

**1a. Remove Render-specific ALLOWED_HOSTS block**

Delete:
```python
RENDER_EXTERNAL_HOSTNAME = env('RENDER_EXTERNAL_HOSTNAME', default=None)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
```

The `ADDITIONAL_ALLOWED_HOSTS` env-var block below it is sufficient — AWS will set it to the CloudFront domain via Secrets Manager.

**1b. Strip the Vercel origin from CORS_ALLOWED_ORIGINS**

Replace:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://resume-builder-frontend-ebon.vercel.app',
]
```
With:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]
```

Rationale: CloudFront serves both the frontend and `/api/*` on the same origin, so no cross-origin request is made in production.

### Verify before merging

- `docker compose up --build` succeeds locally
- `http://localhost:8000/api/schema/swagger-ui/` loads without errors
- No Render env vars are set and server still starts

---

## PR 2 — Terraform Infrastructure

**Goal:** Create all AWS infrastructure (VPC → RDS → ECR → ECS → ALB → CloudFront) as Terraform files. Merge and apply before wiring up CI/CD.

### Pre-apply steps (do these before `terraform apply`, in order)

**Step 1 — Validate the config (no AWS creds needed)**
```bash
cd terraform/
terraform fmt -recursive      # normalise formatting; re-stage any changed files
terraform init -backend=false # download AWS provider plugin only
terraform validate            # should print: Success! The configuration is valid.
```

**Step 2 — Create the tfstate S3 bucket and DynamoDB lock table (one-time, manual)**

These must exist before Terraform can use them as a backend. S3 bucket names are globally unique — replace `<your-account-id>` or pick any unique suffix.

```bash
# Create the tfstate bucket (versioning keeps history of every state change)
aws s3api create-bucket \
  --bucket resume-builder-tfstate-319191253061 \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket resume-builder-tfstate-319191253061 \
  --versioning-configuration Status=Enabled

# Create the DynamoDB lock table (prevents concurrent applies)
aws dynamodb create-table \
  --table-name resume-builder-tfstate-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

**Step 3 — Update `terraform/main.tf` with the backend block** (already done — see Task 2a below)

**Step 4 — Re-run `terraform init` with real backend**
```bash
terraform init   # will prompt to migrate local state to S3 — type "yes"
```

**Step 5 — Set up AWS credentials locally**
```bash
aws configure   # enter Access Key ID, Secret Access Key, region (us-east-1), output (json)
# verify:
aws sts get-caller-identity
```

**Step 6 — Create `terraform/terraform.tfvars`** (git-ignored)
```hcl
db_password       = "a-strong-password-here"
django_secret_key = "a-long-random-string-here"
```
> `terraform.tfvars` is in `.gitignore` — never commit it.

**Step 7 — Preview and apply**
```bash
terraform plan    # review the ~25 resources to be created
terraform apply   # type "yes" to confirm; takes ~5-10 min (RDS is slowest)
```
Note the `cloudfront_url` output when it finishes.

**Step 8 — Bootstrap: push first Docker image to ECR**

ECS can't start until there's an image to pull. Run from the repo root:
```bash
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin <ecr_repository_uri>
docker build -f prod.Dockerfile -t <ecr_repository_uri>:latest .
docker push <ecr_repository_uri>:latest
```

**Step 9 — Update ALLOWED_HOSTS secret**

In the AWS console → Secrets Manager → `resume-builder/backend` → edit the secret value, add the CloudFront domain to `ALLOWED_HOSTS`. Then force a new ECS deployment:
```bash
aws ecs update-service \
  --cluster resume-builder-cluster \
  --service resume-builder-backend \
  --force-new-deployment \
  --region us-east-1
```

---

### Task 2a · `terraform/main.tf`
```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "resume-builder-tfstate-319191253061"
    key            = "backend/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "resume-builder-tfstate-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}
```

### Task 2b · `terraform/variables.tf`
```hcl
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "resume-builder"
}

variable "db_username" {
  type    = string
  default = "postgres"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "django_secret_key" {
  type      = string
  sensitive = true
}

variable "allowed_hosts" {
  description = "Comma-separated ALLOWED_HOSTS — set to CloudFront domain after first apply"
  type        = string
  default     = ""
}
```

### Task 2c · `terraform/outputs.tf`
```hcl
output "cloudfront_url" {
  value = "https://${aws_cloudfront_distribution.main.domain_name}"
}

output "alb_dns" {
  value = aws_lb.main.dns_name
}

output "ecr_repository_uri" {
  value = aws_ecr_repository.backend.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = aws_ecs_service.backend.name
}
```

### Task 2d · `terraform/vpc.tf`
```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "${var.project_name}-vpc" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project_name}-igw" }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "${var.project_name}-public-${count.index}" }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = { Name = "${var.project_name}-private-${count.index}" }
}

resource "aws_eip" "nat" {
  domain = "vpc"
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  tags          = { Name = "${var.project_name}-nat" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = { Name = "${var.project_name}-public-rt" }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }
  tags = { Name = "${var.project_name}-private-rt" }
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

data "aws_availability_zones" "available" {
  state = "available"
}
```

### Task 2e · `terraform/ecr.tf`

> **Bootstrap step:** After `terraform apply` creates the ECR repo, manually push the first image before ECS can run:
> ```bash
> aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ecr_repository_uri>
> docker build -f prod.Dockerfile -t <ecr_repository_uri>:latest .
> docker push <ecr_repository_uri>:latest
> ```

```hcl
resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = { type = "expire" }
    }]
  })
}
```

### Task 2f · `terraform/secrets.tf`
```hcl
resource "aws_secretsmanager_secret" "app" {
  name = "${var.project_name}/backend"
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    DATABASE_URL  = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}/resumebuilder"
    SECRET_KEY    = var.django_secret_key
    ALLOWED_HOSTS = var.allowed_hosts
  })
}

resource "aws_iam_policy" "secrets_read" {
  name = "${var.project_name}-secrets-read"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = aws_secretsmanager_secret.app.arn
    }]
  })
}
```

### Task 2g · `terraform/rds.tf`
```hcl
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_security_group" "rds" {
  name   = "${var.project_name}-rds-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
}

resource "aws_db_instance" "main" {
  identifier             = "${var.project_name}-db"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  db_name                = "resumebuilder"
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot    = true
  publicly_accessible    = false
}
```

### Task 2h · `terraform/alb.tf`
```hcl
resource "aws_security_group" "alb" {
  name   = "${var.project_name}-alb-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "backend" {
  name        = "${var.project_name}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/api/schema/swagger-ui/"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}
```

### Task 2i · `terraform/ecs.tf`
```hcl
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
}

resource "aws_security_group" "ecs_tasks" {
  name   = "${var.project_name}-ecs-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-ecs-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_managed" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_secrets" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.secrets_read.arn
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-ecs-task-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.project_name}-backend"
  retention_in_days = 14
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.project_name}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "backend"
    image     = "${aws_ecr_repository.backend.repository_url}:latest"
    essential = true

    portMappings = [{ containerPort = 8000, protocol = "tcp" }]

    secrets = [
      { name = "DATABASE_URL",  valueFrom = "${aws_secretsmanager_secret.app.arn}:DATABASE_URL::" },
      { name = "SECRET_KEY",    valueFrom = "${aws_secretsmanager_secret.app.arn}:SECRET_KEY::" },
      { name = "ALLOWED_HOSTS", valueFrom = "${aws_secretsmanager_secret.app.arn}:ALLOWED_HOSTS::" },
    ]

    environment = [{ name = "DEBUG", value = "False" }]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/${var.project_name}-backend"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

resource "aws_ecs_service" "backend" {
  name            = "${var.project_name}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]
}
```

### Task 2j · `terraform/s3.tf`
```hcl
resource "aws_s3_bucket" "frontend" {
  bucket = "${var.project_name}-frontend-static"
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = aws_s3_bucket.frontend.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "AllowCloudFront"
      Effect    = "Allow"
      Principal = { Service = "cloudfront.amazonaws.com" }
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.frontend.arn}/*"
      Condition = {
        StringEquals = {
          "AWS:SourceArn" = aws_cloudfront_distribution.main.arn
        }
      }
    }]
  })
}
```

### Task 2k · `terraform/cdn.tf`
```hcl
resource "aws_cloudfront_origin_access_control" "s3" {
  name                              = "${var.project_name}-s3-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "main" {
  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = "S3-frontend"
    origin_access_control_id = aws_cloudfront_origin_access_control.s3.id
  }

  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "ALB-backend"
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # /api/* → ALB, no caching
  ordered_cache_behavior {
    path_pattern           = "/api/*"
    target_origin_id       = "ALB-backend"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Content-Type", "Accept"]
      cookies { forward = "all" }
    }
    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  # /* → S3, cached
  default_cache_behavior {
    target_origin_id       = "S3-frontend"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }

  # SPA fallback
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction { restriction_type = "none" }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
```

### Verify after `terraform apply`

1. `terraform apply` completes with no errors — note the `cloudfront_url` output
2. ECS service shows 1 running task in the AWS console (may take ~2 min after ECR bootstrap)
3. ALB target group shows the task as **healthy**
4. `https://<cloudfront_url>/api/schema/swagger-ui/` returns 200

---

## PR 3 — GitHub Actions CI/CD Workflow

**Goal:** Automate builds and ECS deploys on every push to `main`.

> **Prerequisite:** PR 2 merged and Terraform applied. You'll need the values from `terraform output` to fill in the GitHub secrets.

### Task 3a · Create `.github/workflows/deploy-backend.yml`

```yaml
name: Deploy Backend to ECS

on:

  push:
    branches: [main]

env:
  AWS_REGION: ${{ secrets.AWS_REGION }}
  ECR_REPOSITORY: ${{ secrets.ECR_REPOSITORY_URI }}
  ECS_CLUSTER: ${{ secrets.ECS_CLUSTER }}
  ECS_SERVICE: ${{ secrets.ECS_SERVICE }}

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Log in to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image to ECR
        env:
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -f prod.Dockerfile \
            -t $ECR_REPOSITORY:$IMAGE_TAG \
            -t $ECR_REPOSITORY:latest .
          docker push $ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REPOSITORY:latest

      - name: Force ECS rolling deploy
        run: |
          aws ecs update-service \
            --cluster $ECS_CLUSTER \
            --service $ECS_SERVICE \
            --force-new-deployment
```

### Task 3b · Add GitHub Actions secrets

Set these in **repo Settings → Secrets and variables → Actions**:

| Secret | Where to get the value |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user with ECR push + ECS `update-service` permissions |
| `AWS_SECRET_ACCESS_KEY` | Same IAM user |
| `AWS_REGION` | e.g. `us-east-1` |
| `ECR_REPOSITORY_URI` | `terraform output ecr_repository_uri` |
| `ECS_CLUSTER` | `terraform output ecs_cluster_name` |
| `ECS_SERVICE` | `terraform output ecs_service_name` |

### Verify after merging

1. Push triggers the `Deploy Backend to ECS` workflow in the Actions tab
2. All 5 steps pass (checkout → credentials → ECR login → build+push → force deploy)
3. ECS service shows a new task revision deploying, old task draining
4. `https://<cloudfront_url>/api/schema/swagger-ui/` still returns 200 after deploy completes