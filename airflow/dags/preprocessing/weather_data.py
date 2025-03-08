from datetime import datetime

import pandas as pd
from airflow.exceptions import XComNotFound
from sqlalchemy import text
from utils.common import get_db_connection

CATEGORY = {
    "T1H": "temp",
    "RN1": "rainfall",
    "SKY": "sky_status",
    "UUU": "east_west_wind_component",
    "VVV": "south_north_wind_component",
    "REH": "hum",
    "PTY": "rainfall_type",
    "LGT": "lightning_strike",
    "VEC": "wind_direction",
    "WSD": "wind_speed",
}

RAINFALL_TYPE = {
    "0": None,
    "1": "rain",
    "2": "rain_snow",
    "3": "snow",
    "5": "raindrop",
    "6": "raindrops_of_snow",
    "7": "snowing",
}

def preprocessing(ti):
    weather_data = ti.xcom_pull(task_ids='request_weather_data')
    if not weather_data:
        raise XComNotFound(
            task_id=ti.task_id,
            dag_id=ti.dag_id,
            key='request_weather_data'
        )

    sorted_datas = sorted(weather_data, key=lambda x: (x['fcstDate'], x['fcstTime']))
    preprocessing_datas = []
    for data in sorted_datas:
        category = CATEGORY.get(data.get("category"), "")
        fcst_value = data.get("fcstValue", None)
        if category == "sky_status":
            sky_status = int(fcst_value or 0)
            # sky_status = 맑음(1), 구름조금(2), 구름많음(3), 흐림(4)
            if sky_status == 1:
                fcst_value = "sunny"
            elif sky_status == 2:
                fcst_value = "partly_cloudy"
            elif sky_status == 3:
                fcst_value = "mostly_cloudy"
            elif sky_status == 4:
                fcst_value = "cloudy"
        elif category == "rainfall_type":
            fcst_value = RAINFALL_TYPE.get(fcst_value, "")
        elif category == "rainfall":
            if fcst_value == "강수없음" or "미만" in fcst_value:
                fcst_value = 0
            else:
                fcst_value = float(fcst_value.replace("mm", "").strip())

        forecast_datetime = datetime.strptime(f"{data['fcstDate']} {data['fcstTime']}", "%Y%m%d %H%M")
        timestamp_str = forecast_datetime.strftime("%Y-%m-%d %H:%M:%S")
        preprocessing_datas.append({"forecast_time": timestamp_str, "key": category, "value": fcst_value})

    preprocess_dict = {}
    for data in preprocessing_datas:
        forecast_date = data['forecast_time']
        if forecast_date not in preprocess_dict:
            preprocess_dict[forecast_date] = set()

        preprocess_dict[forecast_date].add((data['key'], data['value']))

    datas = []
    columns = [
        "created_at",
        "updated_at",
        "forecast_time",
        "east_west_wind_component",
        "hum",
        "lightning_strike",
        "rainfall",
        "rainfall_type",
        "sky_status",
        "south_north_wind_component",
        "temp",
        "wind_direction",
        "wind_speed",
    ]
    for forecast_date, data in preprocess_dict.items():
        value_dict = {col: None for col in columns}
        value_dict["forecast_time"] = forecast_date
        value_dict["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        value_dict["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for key, value in data:
            if key in columns:
                value_dict[key] = value

        datas.append(tuple(value_dict[col] for col in columns))

    df = pd.DataFrame(datas, columns=columns)
    ti.xcom_push(key='preprocessed_weather_data', value=df)

def insert_data(ti):
    preprocessed_data = ti.xcom_pull(task_ids='preprocess_data', key='preprocessed_weather_data')
    if preprocessed_data is None:
        raise XComNotFound(
            task_id=ti.task_id,
            dag_id=ti.dag_id,
            key='preprocessed_traffic_data'
        )

    df = pd.DataFrame(preprocessed_data)
    engine = get_db_connection()
    with engine.begin() as conn:
        insert_sql = text("""
            INSERT INTO public.weather_data (
                created_at, updated_at, forecast_time, temp, hum, sky_status, lightning_strike, 
                wind_direction, wind_speed, rainfall, rainfall_type, 
                east_west_wind_component, south_north_wind_component
            ) VALUES (
                :created_at, :updated_at, :forecast_time, :temp, :hum, :sky_status, :lightning_strike, 
                :wind_direction, :wind_speed, :rainfall, :rainfall_type, 
                :east_west_wind_component, :south_north_wind_component
            )
            ON CONFLICT (forecast_time) DO UPDATE SET
                created_at = EXCLUDED.created_at,
                updated_at = EXCLUDED.updated_at,
                temp = EXCLUDED.temp,
                hum = EXCLUDED.hum,
                sky_status = EXCLUDED.sky_status,
                lightning_strike = EXCLUDED.lightning_strike,
                wind_direction = EXCLUDED.wind_direction,
                wind_speed = EXCLUDED.wind_speed,
                rainfall = EXCLUDED.rainfall,
                rainfall_type = EXCLUDED.rainfall_type,
                east_west_wind_component = EXCLUDED.east_west_wind_component,
                south_north_wind_component = EXCLUDED.south_north_wind_component;
        """)
        records = df.to_dict(orient='records')
        conn.execute(insert_sql, records)