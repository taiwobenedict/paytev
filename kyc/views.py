from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import KYC, KYCSettings
from .forms import KYCForm


@login_required
def kyc_view(request):
    try:
        kyc = request.user.kyc
    except KYC.DoesNotExist:
        kyc = None

    # Allow editing if KYC is rejected or not submitted
    if kyc and kyc.status not in ['Not Verified', 'Rejected']:
        return redirect('kyc_status')

    # Fetch KYC settings
    kyc_settings = KYCSettings.objects.first()
    kyc_charge_amount = kyc_settings.kyc_charge_amount if kyc_settings else 0

    if request.method == "POST":
        form = KYCForm(request.POST, instance=kyc)
        if form.is_valid():
            kyc = form.save(commit=False)
            kyc.user = request.user
            kyc.status = 'Submitted'  # Set status to 'Submitted'

            # Check if user has sufficient funds
            if request.user.wallet_credit >= kyc_charge_amount:
                # Deduct KYC charge from user wallet
                request.user.wallet_credit -= kyc_charge_amount
                request.user.save()

                kyc.save()

                # Notify admin about the new KYC submission
                send_mail(
                    'New KYC Submission',
                    f'User {request.user.username} has submitted their KYC details. Please review the submission.',
                    settings.EMAIL_HOST_USER,
                    ['test@paytev.com'],  # Replace with actual admin email
                    fail_silently=False,
                )

                return redirect('kyc_success')
            else:
                # Add an error message to be displayed in the template
                form.add_error(None, 'Insufficient funds to complete KYC submission.')
                return render(request, 'kyc/kyc_form.html', {'form': form, 'kyc_charge_amount': kyc_charge_amount})

    else:
        form = KYCForm(instance=kyc)

    return render(request, 'kyc/kyc_form.html', {'form': form, 'kyc_charge_amount': kyc_charge_amount})



@login_required
def kyc_success(request):
    return render(request, 'kyc/kyc_success.html')



from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.db.models import Q
from .models import KYC

@user_passes_test(lambda u: u.is_superuser)  # Ensure only admin can access this view
@login_required
def kyc_admin_view(request):
    query = request.GET.get('search', '')

    if query:
        kyc_submissions = KYC.objects.filter(
            Q(status='Submitted') & 
            (Q(user__username__icontains=query) | Q(status__icontains=query))
        )
    else:
        kyc_submissions = KYC.objects.filter(status='Submitted')

    return render(request, 'kyc/kyc_admin.html', {'kyc_submissions': kyc_submissions})



@user_passes_test(lambda u: u.is_superuser)  # Ensure only admin can access this view
@login_required
def kyc_action(request, kyc_id):
    kyc = KYC.objects.get(id=kyc_id)

    if request.method == "POST":
        action = request.POST.get('action')
        rejection_reason = request.POST.get('rejection_reason')

        if action == 'verify':
            kyc.status = 'Verified'
            email_subject = 'Your KYC has been verified'
            email_template = 'emails/kyc_verified.html'
            email_context = {'user': kyc.user}
        elif action == 'reject':
            kyc.status = 'Rejected'
            kyc.rejection_reason = rejection_reason
            email_subject = 'Your KYC submission has been rejected'
            email_template = 'emails/kyc_rejected.html'
            email_context = {'user': kyc.user, 'rejection_reason': rejection_reason}

        kyc.save()

        # Notify user about KYC status update
        email_body = render_to_string(email_template, email_context)
        email = EmailMessage(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [kyc.user.email],
        )
        email.content_subtype = "html"  # Make sure to send email as HTML
        email.send(fail_silently=False)
        
        return redirect('kyc_admin_view')

    return render(request, 'kyc/kyc_action.html', {'kyc': kyc})

@login_required
def kyc_status(request):
    try:
        kyc = request.user.kyc
    except KYC.DoesNotExist:
        kyc = None

    # Provide options based on the KYC status
    context = {'kyc': kyc}
    if kyc:
        if kyc.status == 'Rejected':
            context['rejection_reason'] = kyc.rejection_reason
        elif kyc.status == 'Verified':
            context['verification_message'] = 'Account verified successfully'
        elif kyc.status == 'Submitted':
            context['verification_message'] = 'KYC was submitted successfully. Verification in progress'
        else:
            context['verification_message'] = 'Account not yet verified, kindly verify your account'

    return render(request, 'kyc/kyc_status.html', context)



