from django import forms
from django.core.mail import EmailMessage
from livetheatre import settings

CONTACT_SUBJECTS = (
    ('inquiry', 'Personal/website inquiry'),
    ('audition', 'Audition notice'),
    ('production', 'Production notice'),
    ('correction', 'Correction'),
)
class ContactForm(forms.Form):
    """Accepts a message and contact information from the user"""
    subject = forms.ChoiceField(choices=CONTACT_SUBJECTS,
       widget=forms.RadioSelect,
       label='Subject Matter',
       help_text="Please let us know why you're reaching out")
    email = forms.EmailField(label='Email Address',
        help_text='Please provide an address where we can reach you.')
    message = forms.CharField(widget=forms.Textarea)
    attachment = forms.FileField(required=False,
        label='Attach any relevant material',
        help_text='If you have multiple files to attach, please consider '
        'condensing them into a zipped archive.')

    def get_subject(self):
        """Return the subject corresponding to the user's choice"""
        user_email = self.cleaned_data.get('email')
        subjects = {
            'audition': 'Audition Notice from %s' % user_email,
            'production': 'Production Notice from %s' % user_email,
            'inquiry': 'Inquiry from %s' % user_email,
            'default': 'Contact Form Submission from %s' % user_email,
        }

        choice = self.cleaned_data.get('subject')
        choice = choice if choice in subjects.keys() else 'default'
        subject = subjects[choice]
        return subject

    def send_message(self):
        """After form is validated, send the values by email"""
        if not self.cleaned_data:
            self.clean()

        subject = self.get_subject()
        attachment = self.cleaned_data.get('attachment')

        email = EmailMessage(
            subject=self.cleaned_data.get('subject'),
            body=self.cleaned_data.get('message'),
            from_email=self.cleaned_data.get('email'),
            to=settings.DEFAULT_CONTACT_EMAILS)
        if attachment:
            email.attach(attachment.name, attachment.read())
        email.send()
