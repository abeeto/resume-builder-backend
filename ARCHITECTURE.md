# Architecture: Resume Builder on AWS

## Overview

Moving from Render.com (backend) + Vercel (frontend) to AWS. No custom domain — skip Route 53. HTTPS is handled via a single CloudFront distribution that serves both the frontend and proxies API calls (CloudFront provides free `*.cloudfront.net` TLS without a purchased domain).

---

## Traffic Flow

```
Browser
  │
  └─▶ ONE CloudFront distribution (d111.cloudfront.net, HTTPS)
          ├─▶ /api/*  → ALB (HTTP:80, cache TTL=0)
          │               └─▶ ECS Fargate (port 8000, Gunicorn)
          │                       └─▶ RDS PostgreSQL (private subnet)
          └─▶ /*      → S3 bucket (Vite static build, cached)
```

- `/api/*` routes to the ALB with caching disabled; everything else routes to S3.
- Frontend and API share the same `*.cloudfront.net` origin — the browser never makes a cross-origin request, so CORS between frontend and backend is not required in production.
- `VITE_API_BASE_URL` can be an empty string (relative paths just work).

---

## Supporting Services

| Service | Role |
|---|---|
| **ECR** | Private container registry for the Django image |
| **Secrets Manager** | `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_HOSTS` (default AWS-managed KMS key) |
| **VPC** | Public subnets for the ALB, private subnets for ECS + RDS |
| **CloudWatch Logs** | Gunicorn stdout — no code change required |

---

## Terraform File Map

```
terraform/
├── main.tf       # provider config
├── variables.tf  # input variables (region, project name, secrets)
├── outputs.tf    # CloudFront URL, ALB DNS, ECR URI, ECS names
├── vpc.tf        # VPC, subnets, IGW, NAT gateway, route tables
├── rds.tf        # RDS PostgreSQL (private subnet, t3.micro)
├── ecr.tf        # ECR repository + lifecycle policy
├── secrets.tf    # Secrets Manager secret + ECS IAM read policy
├── alb.tf        # ALB, target group (port 8000), HTTP listener
├── ecs.tf        # ECS cluster, task definition, Fargate service, IAM roles
├── s3.tf         # S3 bucket for Vite static files (private, OAC)
└── cdn.tf        # CloudFront: /api/* → ALB, /* → S3
```

---

## Deployment Order

1. `terraform apply` — creates all infrastructure (~25 resources)
2. Note `cloudfront_url` from Terraform outputs (e.g. `https://d111.cloudfront.net`)
3. Bootstrap: manually push first Docker image to ECR (before ECS can pull)
4. Update `ALLOWED_HOSTS` in Secrets Manager to include the CloudFront domain
5. Force new ECS deployment so the container picks up the updated secret
6. Push to `main` on the backend repo → GitHub Actions handles all future deploys
7. Push to `main` on the frontend repo → sync `dist/` to S3 + CloudFront invalidation

---

## Verification Checklist

1. `https://<cloudfront_url>/api/schema/swagger-ui/` — backend is up and Django responds
2. `https://<cloudfront_url>` — frontend loads (after frontend is deployed to S3)
3. Create a resume from the UI — confirm API calls succeed, no CORS or mixed-content errors
4. Push a trivial change to `main` — confirm ECS rolling deploy completes without downtime
5. Check CloudWatch Logs (`/ecs/resume-builder-backend`) for Gunicorn access logs and errors

---

## What's Out of Scope (by design)

- Custom domain / Route 53
- Auto-scaling (can add later via ECS Service Auto Scaling on CPU %)
- Terraform remote state backend (start with local state, add S3 backend later)
- Auth (APIs remain public for now)

---

## Adding Cognito Auth Later

No infrastructure changes are needed — implement at the application level:

1. **Frontend:** Cognito Hosted UI → user logs in → gets JWT access token
2. **Frontend:** Send `Authorization: Bearer <token>` on every API call
3. **CloudFront:** Forward the `Authorization` header on `/api/*` cache behavior (one Terraform line: `headers = ["Authorization"]` — already included in `cdn.tf`)
4. **Django:** Add `django-cognito-jwt` (or `python-jose`) to validate the JWT against Cognito's JWKS endpoint in DRF
5. **Django:** Protect views with `permission_classes = [IsAuthenticated]`

> Do **not** use ALB's built-in Cognito auth — it relies on browser redirects back to the ALB's own URL, which conflicts with the internal ALB setup.