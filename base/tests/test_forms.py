from django.conf import settings
from django.forms import ValidationError
from django.template.defaultfilters import filesizeformat
from django.test import TestCase, override_settings
from mock import patch

from base.forms import ContactForm


class MockAttachment(object):
    """Dummy attachment class for tests"""
    def __init__(self, name='name', size=100):
        self.name = name
        self._size = size

    def read(self):
        pass


class ContactFormTestCase(TestCase):
    def setUp(self):
        self.form = ContactForm()

    @override_settings(MAX_UPLOAD_SIZE='5000')
    def test_clean_attachment(self):
        self.form.cleaned_data = {}
        self.assertIsNone(self.form.clean_attachment())

        small_attachment = MockAttachment(size='400')
        self.form.cleaned_data['attachment'] = small_attachment
        self.assertEqual(self.form.clean_attachment(), small_attachment)

        large_attachment = MockAttachment(size='99999')
        self.form.cleaned_data['attachment'] = large_attachment
        with self.assertRaises(ValidationError) as ctx:
            self.form.clean_attachment()
        self.assertEqual(
            str(ctx.exception),
            str([
                (
                    u'Please keep your attachments smaller than {limit}. '
                    u'This file is {size}'.format(
                        limit=filesizeformat(settings.MAX_UPLOAD_SIZE),
                        size=filesizeformat(large_attachment._size)
                    )
                )
            ])
        )

    def test_get_subject(self):
        self.form.cleaned_data = {
            'email': 'foo@bar.com',
            'subject': 'inquiry',
        }
        self.assertEqual(
            self.form.get_subject(),
            '{prefix}Inquiry from {email}'.format(
                prefix=settings.EMAIL_SUBJECT_PREFIX,
                email='foo@bar.com',
            )
        )

        self.form.cleaned_data['subject'] = 'not-a-subject'
        self.assertEqual(
            self.form.get_subject(),
            '{prefix}Contact Form Submission from {email}'.format(
                prefix=settings.EMAIL_SUBJECT_PREFIX,
                email='foo@bar.com'
            )
        )

    @override_settings(DEFAULT_CONTACT_EMAILS=['foo@bar.com'])
    def test_send_message(self):
        self.form.cleaned_data = {}
        with patch('django.core.mail.EmailMessage.send') as mock_send:
            with patch.object(self.form, 'clean') as mock_clean:
                self.form.send_message()
        mock_clean.assert_called_once_with()
        mock_send.assert_called_once_with()

        attachment = MockAttachment()
        self.form.cleaned_data = {
            'message': 'This is the message.',
            'attachment': attachment,
        }
        with patch('django.core.mail.EmailMessage.send') as mock_send:
            with patch('django.core.mail.EmailMessage.attach') as mock_attach:
                self.form.send_message()
        mock_attach.assert_called_once_with(attachment.name, attachment.read())
        mock_send.assert_called_once_with()
