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
