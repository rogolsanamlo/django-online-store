import threading

_thread_local = threading.local()


def get_current_request():
    """Return the request being handled by the current thread (or None)."""
    return getattr(_thread_local, "current_request", None)


class RequestMiddleware:
    """Stores the current request so model helpers (e.g. Product.get_user_score)
    used from templates can know who the current user is."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_local.current_request = request
        try:
            return self.get_response(request)
        finally:
            _thread_local.current_request = None
