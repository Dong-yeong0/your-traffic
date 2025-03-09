# Metabase Docker Setup

This guide provides step-by-step instructions to set up and run Metabase using Docker. Metabase is an open-source business intelligence tool that allows you to easily visualize and analyze your data.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

* Docker: [Install Docker](https://docs.docker.com/get-started/get-docker/)

* Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Quick Start

Follow these steps to quickly set up and run Metabase using Docker Compose.

1. Set Up the Docker Environment
    Create a `.env` and a `docker-compose.yaml` files with the following content

    ```bash
    vi .env
    ```

    ```bash
    MB_JETTY_PORT=3000
    PORT=3000
    TZ=Asia/Seoul
    # :wq
    ```

    ```bash
    vi docker-compose.yaml
    ```

    ```yaml
    services:
        metabase:
            image: metabase/metabase:latest
            container_name: metabase
            ports:
                - "3000:3000"
            env_file:
                - .env
            volumes:
                - metabase-data:/metabase-data
            restart: always

    volumes:
        metabase-data:
    # :wq
    ```

2. Start Metabase
    Run the following command to start Metabase

    ```bash
    docker-compose up -d
    ```

3. Access Metabase
    Once the container is running, open your browser and navigate to [localhost:3000](http://localhost:3000)

    You should see the Metabase setup screen. Follow the on-screen instructions to complete the setup.
