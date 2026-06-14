terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "resume-builder-tfstate-<your-account-id>"
    key            = "backend/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "resume-builder-tfstate-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}
