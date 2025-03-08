from datetime import datetime, timedelta

import pytz
from airflow.models.variable import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from preprocessing.weather_data import insert_data, preprocessing
from utils.alert import send_fail_alert, send_success_alert

from airflow import DAG

default_args = {
    'owner': 'airflow',
    'retries': 5,
    'retry_delay': timedelta(seconds=30),
    'start_date': datetime.now(pytz.timezone('Asia/Seoul')),
}


with DAG(
    dag_id='weather_data_pipeline',
    default_args=default_args,
    schedule_interval='30 * * * *',
    catchup=False, # 이전 실행 날짜에 대한 DAG 실행을 수행할지 여부 (Default True)
    tags=['weather', 'data', 'api'],
    is_paused_upon_creation=False, # DAG 생성 시 일시중지 여부
    on_success_callback=send_success_alert,
    on_failure_callback=send_fail_alert,
) as dag:
    # HTTP sensor operator를 활용하여 사용할 API가 정상적으로 동작하는지 확인
    weather_api_sensor = HttpSensor(
        task_id='health_check_weather_api',
        http_conn_id='public_data_portal',
        endpoint='1360000/VilageFcstInfoService_2.0/getUltraSrtFcst',
        method='GET',
        request_params={
            "serviceKey": Variable.get('weather_data_api_key'),
            "pageNo": "1",
            "numOfRows": "10",
            "dataType": "JSON",
            "base_date": datetime.now(pytz.timezone('Asia/Seoul')).strftime("%Y%m%d"),
            "base_time": datetime.now(pytz.timezone('Asia/Seoul')).strftime("%H") + "00",
            "nx": "60",
            "ny": "127",
        },
        # HttpSensor의 response_check는 Bool을 반환하여야 성공/실패로 간주함
        response_check=lambda response: response.json()['response']['header']['resultCode'] == '00',
    )

    # 초단기예보 API 호출
    weather_data_api = HttpOperator(
        task_id='request_weather_data',
        http_conn_id='public_data_portal',
        endpoint='1360000/VilageFcstInfoService_2.0/getUltraSrtFcst',
        method='GET',
        data={
            "serviceKey": Variable.get('weather_data_api_key'),
            "pageNo": "1",
            "numOfRows": "10",
            "dataType": "JSON",
            "base_date": datetime.now(pytz.timezone('Asia/Seoul')).strftime("%Y%m%d"),
            "base_time": datetime.now(pytz.timezone('Asia/Seoul')).strftime("%H") + "00",
            "nx": "60",
            "ny": "127",
        },
        response_filter=lambda response: response.json()['response']['body']['items']['item'],
        log_response=True,
    )

    # 데이터 전처리
    preprocess_data = PythonOperator(
        task_id='preprocess_data',
        python_callable=preprocessing,
    )

    # DB에 저장하기
    insert_data = PythonOperator(
        task_id='insert_data',
        python_callable=insert_data,
    )

    weather_api_sensor >> weather_data_api >> preprocess_data >> insert_data