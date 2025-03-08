from datetime import datetime, timedelta

import pandas as pd
import pytz
import requests
from airflow.exceptions import XComNotFound
from airflow.models.taskinstance import TaskInstance
from airflow.models.variable import Variable
from sqlalchemy import text
from utils.common import camel_to_snake, get_db_connection


def request_traffic_data_by_unit(ti: TaskInstance):
    """ 고속도로 단위별 교통량 데이터를 API에서 요청하여 가져오는 함수 """

    URL = "https://data.ex.co.kr/openapi/odtraffic/trafficAmountByUnit"
    KEY = Variable.get("traffic_data_api_key")
    params = {
        'key': KEY,
        'type': 'json',
        'sumTmUnitTypeCode': '3',
        'stdHour': (datetime.now(pytz.timezone('Asia/Seoul')) - timedelta(hours=2)).strftime('%H'),
        'numOfRows': '99',
    }
    data = []
    try:
        res = requests.get(URL, params=params, timeout=60)
        res.raise_for_status()
        res_json: dict = res.json()

        if res_json.get('code') != 'SUCCESS':
            ti.log.error(f"API response error: {res_json.get('message', 'Unknown error')}")
            return

        data.extend(res_json.get('list', []))
        page_size = res_json.get('pageSize')
        for i in range(2, page_size + 1):
            params['pageNo'] = i
            res = requests.get(URL, params=params, timeout=60)
            res.raise_for_status()
            res_json: dict = res.json()
            data.extend(res_json.get('list', []))
            ti.log.info(f"Page {i} fetched, fetched data length: {len(res_json.get('list'))}")

        ti.log.info(f"Total {len(data)} traffic data entries fetched successfully")
        ti.xcom_push(key='traffic_data_by_unit', value=data)

    except requests.exceptions.Timeout:
        ti.log.error("API request timed out")
        return
    except requests.exceptions.HTTPError as e:
        ti.log.error(f'HTTP error occurred while requesting traffic data: {e}')
        return
    except requests.exceptions.RequestException as e:
        ti.log.error(f'Error occurred while requesting traffic data: {e}')
        return

def preprocessing_data(ti: TaskInstance):
    data = ti.xcom_pull(key='traffic_data_by_unit')
    df = pd.DataFrame(data)
    df.columns = [camel_to_snake(c) for c in df.columns]
    # Remove unused columns
    df.drop(columns=['page_no', 'num_of_rows'], inplace=True)

    # Rename the column (traffic_amout -> traffic_amount)
    df.rename(columns={'traffic_amout': 'traffic_amount'}, inplace=True)

    # Change datetime format
    df['std_hour'] = df['std_hour'].str.strip()
    df['std_date_str'] = df['std_date'] + ' ' + df['std_hour'] + ':00:00'
    df['std_date'] = pd.to_datetime(df['std_date_str'], format='%Y%m%d %H:%M:%S')
    df.drop(columns=['std_date_str'], inplace=True)

    ti.xcom_push(key='preprocessed_traffic_data_by_unit', value=df)
    return df

def insert_data(ti: TaskInstance):
    preprocessed_data = ti.xcom_pull(key='preprocessed_traffic_data_by_unit')
    if preprocessed_data is None:
        raise XComNotFound(
            task_id=ti.task_id,
            dag_id=ti.dag_id,
            key='preprocessed_traffic_data_by_unit'
        )

    engine = get_db_connection()
    with engine.begin() as conn:
        insert_query = text('''
            INSERT INTO public.traffic_data_by_unit (
                unit_name, unit_code, std_date, traffic_amount, inout_name, center_code, center_name, sum_tm_unit_type_code, start_end_std_type_code, tcs_car_type_cd, brof_code, brof_name, tcs_car_type_nm, tcs_car_type_grp_nm, tcs_car_type_grp_cd
            ) VALUES (
                :unit_name, :unit_code, :std_date, :traffic_amount, :inout_name, :center_code, :center_name, :sum_tm_unit_type_code, :start_end_std_type_code, :tcs_car_type_cd, :brof_code, :brof_name, :tcs_car_type_nm, :tcs_car_type_grp_nm, :tcs_car_type_grp_cd
            ) ON CONFLICT (unit_code, std_date, inout_name, tcs_car_type_cd) 
            DO UPDATE SET 
                unit_name = EXCLUDED.unit_name,
                traffic_amount = EXCLUDED.traffic_amount,
                inout_name = EXCLUDED.inout_name,
                center_code = EXCLUDED.center_code,
                center_name = EXCLUDED.center_name,
                sum_tm_unit_type_code = EXCLUDED.sum_tm_unit_type_code,
                start_end_std_type_code = EXCLUDED.start_end_std_type_code,
                tcs_car_type_cd = EXCLUDED.tcs_car_type_cd,
                brof_code = EXCLUDED.brof_code,
                brof_name = EXCLUDED.brof_name,
                tcs_car_type_nm = EXCLUDED.tcs_car_type_nm,
                tcs_car_type_grp_nm = EXCLUDED.tcs_car_type_grp_nm,
                tcs_car_type_grp_cd = EXCLUDED.tcs_car_type_grp_cd;

        ''')
        records = preprocessed_data.to_dict(orient='records')
        conn.execute(insert_query, records)
