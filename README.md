# Resume Builder Backend

This repository contains the backend for the Pavetheway.ai resume builder application. It is built using Django REST Framework and a PostgreSQL database, and is designed to handle the progressive profile completion flow and resume data management.

## Tech Stack

- **Backend**: Django REST Framework
- **Database**: PostgreSQL
- **Containerization**: Docker
- **Deployment**: Render

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
Using Swagger API, to see the api on deployed server visit: 
  `https://resume-builder-backend-atlm.onrender.com/api/schema/swagger-ui`


To see the API docs on localhost visit:
    `http://localhost:8000/api/schema/swagger-ui`

---

## Deployment

_Details on how to deploy the backend to Render will be added here._
