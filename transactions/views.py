from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from transactions.models import Transactions

@login_required(login_url=settings.LOGIN_URL)
def transactions(request):
    # Determine the page number and search term from the request
    search_term = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)

    # Fetch transactions based on user permissions
    if request.user.is_superuser:
        transactions = Transactions.objects.all().order_by("-created_at")
    else:
        transactions = Transactions.objects.filter(user=request.user).order_by("-created_at")

    # Apply search filter if a search term is provided
    if search_term:
        transactions = transactions.filter(
            Q(reference__icontains=search_term) |
            Q(bill_number__icontains=search_term) |
            Q(status__icontains=search_term) |
            Q(bill_type__icontains=search_term)
        )

    # Paginate transactions
    paginator = Paginator(transactions, 20)  # Show 20 transactions per page
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Pass the transactions and search term to the template
    context = {
        'transactions': page_obj,
    }
    return render(request, "transactions/history.html", context)

@login_required(login_url=settings.LOGIN_URL)
def transactions_details(request, reference):
    # Fetch and return transaction details based on reference
    transaction = get_object_or_404(Transactions, reference=reference)
    return render(request, "i/transaction_details.html", {"transaction": transaction})

@login_required(login_url=settings.LOGIN_URL)
def transaction_list(request):
    # Determine the page number from the request
    search_term = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)

    # Fetch transactions based on user permissions
    if request.user.is_superuser:
        transactions = Transactions.objects.all().order_by("-created_at")
    else:
        transactions = Transactions.objects.filter(user=request.user).order_by("-created_at")

    if search_term:
        transactions = transactions.filter(
            Q(reference__icontains=search_term) |
            Q(bill_number__icontains=search_term) |
            Q(status__icontains=search_term) |
            Q(bill_type__icontains=search_term)
        )

    # Paginate transactions
    paginator = Paginator(transactions, 50)  # Show 50 transactions per page
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Prepare response data
    data = {
        'transactions': list(page_obj.object_list.values(
            'id', 'reference', 'bill_number', 'created_at', 'status', 'paid_amount', 'bill_type'
        )),
        'has_next': page_obj.has_next(),
        'total_count': transactions.count(),
    }
    return JsonResponse(data)

@login_required(login_url=settings.LOGIN_URL)
def transactions_details(request, reference):
    # Fetch and return transaction details based on reference
    obj = Transactions.objects.get(reference=reference)
    response = None
    if obj.api_response:
        response = obj.api_response
    return render(request, "transactions/details.html", {"data": obj, "response": response})

@login_required(login_url=settings.LOGIN_URL)
def transactions_failed(request, reference):
    # Fetch and return transaction details for failed transactions
    obj = Transactions.objects.get(reference=reference)
    response = None
    if obj.api_response:
        response = obj.api_response
    return render(request, "i/failed.html", {"data": obj, "response": response})
