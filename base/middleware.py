import pytz
from django.utils import timezone


class TexasTimezoneMiddleware(object):
    """Middleware to activate US/Central timezone, unless otherwise specified"""
    def process_request(self, request):
        tzname = request.session.get('timezone', 'US/Central')
        timezone.activate(pytz.timezone(tzname))
