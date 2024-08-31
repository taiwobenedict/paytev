from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BulkEmailForm
from .models import SentEmail

def send_bulk_email(request):
    if request.method == 'POST':
        form = BulkEmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            recipients = User.objects.all()

            # Send email
            send_mail(
                subject,
                body,
                'test@paytev.com',
                [user.email for user in recipients],
                fail_silently=False,
            )

            # Save email to SentEmail model
            email_record = SentEmail.objects.create(
                subject=subject,
                body=body,
            )
            email_record.recipients.set(recipients)
            email_record.save()

            messages.success(request, 'Email sent successfully!')
            return redirect('send_bulk_email')
    else:
        form = BulkEmailForm()

    return render(request, 'emails/send_bulk_email.html', {'form': form})
