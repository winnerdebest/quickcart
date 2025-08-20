import requests
from django.conf import settings

NOTIFY_EVENTS_URL = "https://notify.events/api/v1/channel/source/{}/execute"

def send_notify_event(message, title="🚨 Django Alert"):
    """
    Sends a notification to Notify.Events channel via Source token
    """
    token = getattr(settings, "NOTIFY_EVENTS_SOURCE", None)  # source token
    if not token:
        raise ValueError("NOTIFY_EVENTS_SOURCE not set in settings.py")

    url = NOTIFY_EVENTS_URL.format(token)

    payload = {
        "title": title,
        "text": message,
        "priority": "normal",
        "level": "info",
    }

    try:
        requests.post(url, data=payload, timeout=5)
    except requests.RequestException as e:
        print("Notify.Events error:", e)