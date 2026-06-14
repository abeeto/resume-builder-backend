# Backend Migration Plan: Render → AWS ECS Fargate

Scope: all tasks are within this repo (`resume-builder-backend`).  
Architecture context lives in [ARCHITECTURE.md](ARCHITECTURE.md).

## Constraints
- No Git pushes or PRs — hand off to human whenever a push/PR is needed
- Do not list Claude as co-author
- Commit messages follow conventional commits
- Every PR/feature on its own branch

---

## PR 1 — Django Settings Cleanup [DONE]

Branch: `pr/1-django-settings-cleanup`

Removed Render/Vercel coupling from `settings.py`:
- Deleted the `RENDER_EXTERNAL_HOSTNAME` block — replaced by `ADDITIONAL_ALLOWED_HOSTS` env var (comma-separated, split at startup)
- Removed Vercel origin from `CORS_ALLOWED_ORIGINS` — not needed since CloudFront serves both frontend and `/api/*` on the same origin

---

## PR 2 — Terraform Infrastructure [DONE]

Branch: `pr/2-terraform-infrastructure`

### What was built

11 Terraform files create the full AWS stack (~40 resources):

- **VPC** (`vpc.tf`) — `10.0.0.0/16`, 2 public subnets (ALB), 2 private subnets (ECS + RDS), NAT gateway for outbound traffic from private subnets
- **ECR** (`ecr.tf`) — private Docker registry `resume-builder-backend`, scan on push, lifecycle policy keeping last 10 images
- **Secrets Manager** (`secrets.tf`) — secret `resume-builder/backend` holds `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_HOSTS` as JSON; IAM policy grants ECS execution role `GetSecretValue`
- **RDS** (`rds.tf`) — PostgreSQL 16, `db.t3.micro`, 20GB, private subnets only, port 5432 open only to ECS security group
- **ALB** (`alb.tf`) — public subnets, target group port 8000 `target_type=ip` (required for Fargate), health check on `/api/schema/swagger-ui/`
- **ECS** (`ecs.tf`) — Fargate cluster, task definition (256 CPU / 512MB), secrets injected from Secrets Manager at startup, `DEBUG=False`, CloudWatch logs 14-day retention, service in private subnets
- **S3** (`s3.tf`) — `resume-builder-frontend-static`, all public access blocked, accessible only via CloudFront OAC
- **CloudFront** (`cdn.tf`) — single distribution, `/api/*` → ALB (no cache, forwards Authorization/Content-Type/Accept/cookies), `/*` → S3 (cached, 86400s default), 403→200 SPA fallback

### Remote state

tfstate stored in S3 bucket `resume-builder-tfstate-319191253061` (created manually via AWS CLI before first `terraform init`). Locking via `use_lockfile = true` in the S3 backend — no DynamoDB table needed.

### Key decisions and gotchas

- **`use_lockfile = true`** — replaces the deprecated `dynamodb_table` approach; lock file stored in the same S3 bucket
- **`recovery_window_in_days = 0`** on the Secrets Manager secret — without this, `terraform destroy` + re-apply within 30 days fails because the secret name is reserved
- **ALLOWED_HOSTS needs both CloudFront domain AND ALB DNS name** — CloudFront replaces the Host header with the ALB domain when forwarding to the origin, so Django sees the ALB hostname, not the CloudFront domain. Secret value must be: `d3j7ddovj71i1i.cloudfront.net,resume-builder-alb-1600685865.us-east-1.elb.amazonaws.com`
- **`aws login` credentials** — browser-based AWS CLI v2 flow stores tokens in `~/.aws/login/cache`. These are NOT in Terraform's credential chain. Each session requires: `aws configure export-credentials --profile resume-builder-tf --format env` then paste the 4 exported env vars. Tokens last ~1 hour — refresh before long applies
- **Docker image** — use `prod.Dockerfile` (not `Dockerfile` or `local.Dockerfile`). Build from repo root: `docker build -f prod.Dockerfile`
- **ECS starts with `runningCount=0`** — normal for a few minutes after force-deploy while the task pulls the image and passes the health check

### Live values

| Output | Value |
|---|---|
| CloudFront URL | `https://d3j7ddovj71i1i.cloudfront.net` |
| ALB DNS | `resume-builder-alb-1600685865.us-east-1.elb.amazonaws.com` |
| ECR URI | `319191253061.dkr.ecr.us-east-1.amazonaws.com/resume-builder-backend` |
| ECS Cluster | `resume-builder-cluster` |
| ECS Service | `resume-builder-backend` |
| RDS Endpoint | `resume-builder-db.ce5ks8ii0gtk.us-east-1.rds.amazonaws.com` |

### Verify

`https://d3j7ddovj71i1i.cloudfront.net/api/schema/swagger-ui/` returns 200 ✓

---

## PR 3 — GitHub Actions CI/CD Workflow [TODO]

Branch: `pr/3-github-actions-cicd`

### Goal

Automate build + ECS deploy on every push to `main` so `docker build`, `docker push`, and `aws ecs update-service` never need to be run manually again.

### What to create

**`.github/workflows/deploy-backend.yml`** — on push to `main`:
1. Configure AWS credentials (from GitHub secrets)
2. Log in to ECR
3. `docker build -f prod.Dockerfile`, tag with both `${{ github.sha }}` and `latest`, push both tags
4. `aws ecs update-service --force-new-deployment`

### GitHub Actions secrets needed

Create an IAM user with ECR push + ECS `update-service` permissions, then add to repo Settings → Secrets and variables → Actions:

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | `us-east-1` |
| `ECR_REPOSITORY_URI` | `319191253061.dkr.ecr.us-east-1.amazonaws.com/resume-builder-backend` |
| `ECS_CLUSTER` | `resume-builder-cluster` |
| `ECS_SERVICE` | `resume-builder-backend` |

### Verify after merging

1. Push triggers `Deploy Backend to ECS` workflow in the Actions tab
2. All steps pass — confirm new task revision deploys and old task drains
3. `https://d3j7ddovj71i1i.cloudfront.net/api/schema/swagger-ui/` still returns 200
