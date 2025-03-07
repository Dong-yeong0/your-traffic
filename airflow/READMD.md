# Setting Up Airflow with Docker Compose

> Ref: [Running Airflow in Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)

To set up Apache Airflow using Docker Compose, you can easily fetch the official Docker Compose file using `curl`. Follow the steps below

1. **Download the Docker Compose file**

    Run the following command to download the official Docker Compose file

    ```bash
    curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.5/docker-compose.yaml'
    ```

    If your os is Windows, run the following command

    ```powershell
    Invoke-WebRequest -Uri https://airflow.apache.org/docs/apache-airflow/2.10.5/docker-compose.yaml -OutFile 'docker-compose.yaml'
    ```

2. Initializing environment

    ```bash
    vi docker-compose.yaml
    ```

    ```bash
    # Change true to false in AIRFLOW__CORE__LOAD_EXAMPLES environment variable
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false' # true -> false

    # and uncomment the following line (if you want to customize the environment)
    AIRFLOW_CONFIG: '/opt/airflow/config/airflow.cfg'

    # :wq
    ```

    ```bash
    mkdir -p ./dags ./logs ./plugins ./config
    echo -e "AIRFLOW_UID=$(id -u)" > .env
    ```

    ```bash
    docker compose up airflow-init
    ```

3. Start Airflow
    After downloading the Docker Compose file, you can start Airflow by running

    ```bash
    docker compose up -d
    ```

4. Access the Airflow web interface

    Once the services are up and running, you can access the Airflow web interface by navigating to [http://localhost:8080](http://localhost:8080) in your web browser. (default id: `airflow`, password: `airflow`)
