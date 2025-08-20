from .utils.notifications import send_notify_event

class VisitorNotificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only notify once per session
        if not request.session.get("visitor_notified", False):
            ip = request.META.get("REMOTE_ADDR")
            path = request.path
            send_notify_event(f"👤 New visitor at {path} from {ip}", "New Visitor")
            request.session["visitor_notified"] = True  # mark session as notified

        return response