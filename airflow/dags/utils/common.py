import re

from airflow.hooks.base import BaseHook
from sqlalchemy import create_engine


def get_db_connection():
    conn_id = 'traffic_db'
    conn = BaseHook.get_connection(conn_id)
    uri = conn.get_uri()
    if uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql://', 1)

    return create_engine(uri)


def camel_to_snake(col):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', col).lower()