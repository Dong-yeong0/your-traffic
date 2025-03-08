import pytz
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

SLACK_WEBHOOK_CONN_ID = "slack_incoming_webhook"
def send_message(slack_msg, context, title, color):
    return SlackWebhookOperator(
        slack_webhook_conn_id=SLACK_WEBHOOK_CONN_ID,
        task_id="slack_alert",
        message=slack_msg,
        username="airflow",
        attachments=[
            {
                "mrkdwn_in": ["text"],
                "title": title,
                "actions": [
                    {
                        "type": "button",
                        "name": "view log",
                        "text": "View log",
                        "url": context.get("task_instance").log_url,
                        "style": "danger" if color == "danger" else "default",
                    },
                ],
                "color": color,  # 'good', 'warning', 'danger', or hex ('#439FE0')
                "fallback": "details",  # Required plain-text summary of the attachment
            }
        ]
    )

def send_fail_alert(context):
    execution_date_utc = context.get('execution_date')
    execution_date_seoul = execution_date_utc.astimezone(pytz.timezone('Asia/Seoul'))
    slack_msg = f"""
    :red_circle: Task Failed.
    *Task*: {context.get("task_instance").task_id}
    *Dag*: {context.get("task_instance").dag_id}
    *Execution Time*: {execution_date_seoul.strftime("%Y-%m-%d %H:%M:%S %z")}
    """
    alert = send_message(slack_msg, context, title="Task Failure", color="danger")
    return alert.execute(context=context)

def send_success_alert(context):
    execution_date_utc = context.get('execution_date')
    execution_date_seoul = execution_date_utc.astimezone(pytz.timezone('Asia/Seoul'))
    slack_msg = f"""
    :large_green_circle: Task Succeeded.
    *Task*: {context.get("task_instance").task_id}
    *Dag*: {context.get("task_instance").dag_id}
    *Execution Time*: {execution_date_seoul.strftime('%Y-%m-%d %H:%M:%S %z')}
    """
    alert = send_message(slack_msg, context, title="Task Success", color="good")
    return alert.execute(context=context)