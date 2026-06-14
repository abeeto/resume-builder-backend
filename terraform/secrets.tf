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
