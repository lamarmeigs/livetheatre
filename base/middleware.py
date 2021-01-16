import pytz
from django.utils import deprecation, timezone


class TexasTimezoneMiddleware(deprecation.MiddlewareMixin):
    """Middleware to activate US/Central timezone, unless otherwise specified"""
    def process_request(self, request):
        tzname = request.session.get('timezone', 'US/Central')
        timezone.activate(pytz.timezone(tzname))
