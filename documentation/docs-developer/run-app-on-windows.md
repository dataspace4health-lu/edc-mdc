---
sidebar_position: 6
sidebar_label: Run app on Windows
---

# Run app on Windows

Run the Metadata Capture application locally on a Windows machine using Docker Compose for a self-contained environment with PostgreSQL database and Keycloak IAM.

## Prerequisites

Ensure you have the following tools installed:

- **Git:** Version control system
- **Docker Desktop for Windows:** For running containerized services

## Navigate to the project directory

Navigate to the cloned repository:

```bash
cd dca-metadata-capture
```

## Build and launch the environment

1. Build the Docker image:

   ```bash
   docker compose -f docker-compose.win.yaml build
   ```

2. Launch the environment:

   ```bash
   docker compose -f docker-compose.win.yaml up
   ```

3. In a new terminal, execute database migrations to prepare the system:

   ```bash
   docker compose -f docker-compose.win.yaml exec -e LOAD_INITIAL_DATA=True app alembic upgrade head
   ```

   This configuration will deploy both a PostgreSQL database and a Keycloak IAM as Docker containers along with the main application, creating a self-contained testing environment.

## Access the application

Once operational, the application can be accessed at **http://localhost:8000**.

### Login credentials

You can log in using:

- **Email:** ami@lnds.lu
- **Password:** test

### Keycloak admin console

To manage users or change Keycloak settings, access the Keycloak admin console at **http://localhost:8080** using:

- **Username:** admin
- **Password:** admin
