from django import template
from strowallet.models import StrowalletAccount

register = template.Library()

@register.inclusion_tag('strowallet/view_account.html', takes_context=True)
def load_account_details(context):
    request = context['request']
    account = StrowalletAccount.objects.filter(user=request.user).first()
    return {'account': account}
