# app/routers/v1/tasks.py
import smtplib
from email.message import EmailMessage
from celery import shared_task
from app.settings import settings


def _send_mail_smtp(to: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        # 如果是 587 走 STARTTLS；如果是 465 就用 smtplib.SMTP_SSL 改造
        try:
            server.starttls()
        except smtplib.SMTPNotSupportedError:
            # 有的服务商端口不需要/不支持 STARTTLS
            pass
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)


@shared_task(
    autoretry_for=(smtplib.SMTPException, TimeoutError, ConnectionError),
    retry_backoff=5,  # 指数退避（5s, 10s, 20s...）
    retry_kwargs={"max_retries": 5},
    acks_late=True,  # 防止 worker 崩溃导致消息丢失
)
def send_email_task(to: str, subject: str, body: str) -> dict:
    """
    发送邮件的 Celery 任务；失败会自动重试。
    返回一个简短的结果字典便于前端查看。
    """
    print(to, subject, body)
    _send_mail_smtp(to, subject, body)
    return {"status": "sent", "to": to}


@shared_task
def add(a, b):
    return a + b
