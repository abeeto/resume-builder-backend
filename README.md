# Resume Builder Backend

It is built using Django REST Framework and a PostgreSQL database, and is designed to handle the progressive profile completion flow and resume data management.

## Tech Stack

- **Backend**: Django REST Framework
- **Database**: PostgreSQL
- **Containerization**: Docker
- **Deployment**: AWS ECS Fargate + CloudFront

## Local Development
    To run django app and local postgres db on a container for testing/development

  ### 1. Copy environment settings
  `cp .env.example .env`

  ### 2. Start the entire stack
  `docker compose up`

  ### Or rebuild and start
  `docker compose up --build`

  ### To update database:
  `docker compose up -d`
  `docker exec web python manage.py makemigrations`
  `docker exec web python manage.py migrate`

  ### To end session:
  `docker compose down`

  ### To clear out database
  `docker compose down --volumes`



---

## API Documentation

Swagger UI on localhost:

  `http://localhost:8000/api/schema/swagger-ui`

---

## Deployment

The backend runs on AWS ECS Fargate behind a CloudFront distribution.

- Architecture and infrastructure overview: [ARCHITECTURE.md](ARCHITECTURE.md)
- Migration plan and PR breakdown: [PLAN.md](PLAN.md)
