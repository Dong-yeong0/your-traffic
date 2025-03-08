from datetime import datetime, timedelta

import pytz
from airflow.models.variable import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from preprocessing.traffic_data import (
    insert_data,
    preprocessing_data,
    request_traffic_data_by_unit,
)
from utils.alert import send_fail_alert, send_success_alert

from airflow import DAG

default_args = {
    'owner': 'airflow',
    'retries': 5,
    'retry_delay': timedelta(seconds=10),
}

with DAG(
    dag_id='traffic_data_by_unit_pipeline',
    schedule_interval='10 * * * *',
    catchup=False,
    start_date=datetime(2025, 3, 7),
    description='Traffic data by unit pipeline',
    tags=['traffic', 'api'],
    on_success_callback=send_success_alert,
    on_failure_callback=send_fail_alert,
    default_args=default_args
) as dag:
    # API health check
    api_health_check = HttpSensor(
        task_id='traffic_data_by_unit_api_health_check',
        http_conn_id='traffic_data_open_api_base_url',
        endpoint='/openapi/odtraffic/trafficAmountByUnit',
        request_params={
            'key': Variable.get('traffic_data_api_key'),
            'type': 'json',
            'sumTmUnitTypeCode': '3',
            'stdHour': (datetime.now(pytz.timezone('Asia/Seoul')) - timedelta(hours=2)).strftime('%H'),
        },
        method='GET',
        response_check=lambda response: response.status_code == 200
    )

    # Traffic data by unit API call
    traffic_data_by_unit_api_call = PythonOperator(
        task_id='traffic_data_by_unit_api_call',
        python_callable=request_traffic_data_by_unit
    )

    # Preprocessing and insertion of traffic data
    preprocessing_data_by_unit = PythonOperator(
        task_id='preprocessing_data_by_unit',
        python_callable=preprocessing_data
    )

    # Insert data to db
    insert_traffic_data_by_unit = PythonOperator(
        task_id='insert_traffic_data_by_unit',
        python_callable=insert_data
    )

    api_health_check >> traffic_data_by_unit_api_call >> preprocessing_data_by_unit >> insert_traffic_data_by_unit