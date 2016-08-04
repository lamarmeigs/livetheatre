import pytz

from django.http import HttpRequest
from django.test import TestCase
from django.utils import timezone
from mock import patch

from base.middleware import TexasTimezoneMiddleware


class TexasTimezoneMiddlewareTestCase(TestCase):
    def test_process_request(self):
        request = HttpRequest()
        request.session = {}
        middleware = TexasTimezoneMiddleware()
        with patch.object(pytz, 'timezone') as mock_timezone:
            with patch.object(timezone, 'activate'):
                middleware.process_request(request)
        mock_timezone.assert_called_once_with('US/Central')

        request.session = {'timezone': 'US/Eastern'}
        with patch.object(pytz, 'timezone') as mock_timezone:
            with patch.object(timezone, 'activate'):
                middleware.process_request(request)
        mock_timezone.assert_called_once_with('US/Eastern')
