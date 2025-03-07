# Docker-based PostgreSQL Setup

This repository contains configuration files for setting up a PostgreSQL database using Docker.

## Prerequisites

- Docker installed on your machine
- Docker Compose (optional, but recommended for multi-container setups)

## Getting Started

Follow these steps to set up PostgreSQL using Docker:

1. Create or modify the ".env" file

    ```bash
    vi .env
    ```

    ```env
    POSTGRES_USER=changeme
    POSTGRES_PASSWORD=changeme
    POSTGRES_DB=postgres
    PORT=5432
    ```

2. **Run the container with Docker Compose**

    ```bash
    docker compose up -d
    ```

3. **Access PostgreSQL**

    ```bash
    docker exec -it <your_postgres_container> psql -U <your_username> -d <your_database>
    ```
