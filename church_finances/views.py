from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.messages import success, error, info
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Transaction, Member, Tithing
from .forms import CustomUserCreationForm, TransactionForm, MemberForm, TithingForm, TithingFilterForm
from django.contrib.auth.forms import AuthenticationForm  # For login form
from datetime import datetime


def register_view(request):
    """
    Handles user registration.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in immediately after registration
            success(request, "Registration successful! You are now logged in.")
            return redirect("dashboard")
        else:
            for field, errors_list in form.errors.items():
                for err in errors_list:
                    error(request, f"{field}: {err}")
    else:
        form = CustomUserCreationForm()
    return render(request, "church_finances/register.html", {"form": form})


def user_login_view(request):
    """
    Handles user login.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            success(request, f"Welcome back, {user.username}!")
            return redirect("dashboard")
        else:
            error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "church_finances/login.html", {"form": form})


@login_required
def user_logout_view(request):
    """
    Handles user logout.
    """
    logout(request)
    info(request, "You have been logged out.")
    return redirect("home")


@login_required
def dashboard_view(request):
    """
    Displays a financial summary dashboard.
    """
    total_income = (
        Transaction.objects.filter(type="income").aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0
    )
    total_expense = (
        Transaction.objects.filter(type="expense").aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0
    )
    net_balance = total_income - total_expense

    recent_transactions = Transaction.objects.all()[:10]  # Display last 10 transactions

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance,
        "recent_transactions": recent_transactions,
    }
    return render(request, "church_finances/dashboard.html", context)


@login_required
def transaction_list_view(request):
    """
    Displays a list of all financial transactions.
    """
    transactions = Transaction.objects.all()
    context = {"transactions": transactions}
    return render(request, "church_finances/transaction_list.html", context)


@login_required
def transaction_create_view(request):
    """
    Handles creation of new financial transactions.
    """
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.recorded_by = (
                request.user
            )  # Assign the current user as recorder
            transaction.save()
            success(request, "Transaction added successfully!")
            return redirect("transaction_list")
        else:
            for field, errors_list in form.errors.items():
                for err in errors_list:
                    error(request, f"{field}: {err}")
    else:
        form = TransactionForm()
    return render(
        request,
        "church_finances/transaction_form.html",
        {"form": form, "title": "Add New Transaction"},
    )


@login_required
def transaction_detail_view(request, pk):
    """
    Displays details of a single transaction.
    """
    transaction = get_object_or_404(Transaction, pk=pk)
    context = {"transaction": transaction}
    return render(request, "church_finances/transaction_detail.html", context)


@login_required
def transaction_update_view(request, pk):
    """
    Handles updating an existing financial transaction.
    """
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            success(request, "Transaction updated successfully!")
            return redirect("transaction_detail", pk=pk)
        else:
            for field, errors_list in form.errors.items():
                for err in errors_list:
                    error(request, f"{field}: {err}")
    else:
        form = TransactionForm(instance=transaction)
    return render(
        request,
        "church_finances/transaction_form.html",
        {"form": form, "title": "Update Transaction"},
    )


@login_required
def transaction_delete_view(request, pk):
    """
    Handles deletion of a financial transaction.
    """
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        transaction.delete()
        success(request, "Transaction deleted successfully!")
        return redirect("transaction_list")
    return render(
        request, "church_finances/confirm_delete.html", {"transaction": transaction}
    )


# Member Management Views
@login_required
def member_list_view(request):
    """
    Displays a list of all church members.
    """
    members = Member.objects.filter(is_active=True).order_by('last_name', 'first_name')
    context = {'members': members}
    return render(request, 'church_finances/member_list.html', context)


@login_required
def member_create_view(request):
    """
    Handles creation of new church members.
    """
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            success(request, f'Member {member.full_name} added successfully!')
            return redirect('member_list')
        else:
            for field, errors_list in form.errors.items():
                for err in errors_list:
                    error(request, f'{field}: {err}')
    else:
        form = MemberForm()
    return render(request, 'church_finances/member_form.html', {'form': form, 'title': 'Add New Member'})


@login_required
def member_detail_view(request, pk):
    """
    Displays details of a single member with their tithing history.
    """
    member = get_object_or_404(Member, pk=pk)
    tithes = member.tithes.filter(is_active=True).order_by('-date')
    
    # Calculate yearly totals
    current_year = datetime.now().year
    yearly_totals = {}
    for year in range(current_year - 4, current_year + 1):
        yearly_totals[year] = member.total_tithes(year)
    
    context = {
        'member': member,
        'tithes': tithes,
        'yearly_totals': yearly_totals,
        'total_all_time': member.total_tithes()
    }
    return render(request, 'church_finances/member_detail.html', context)


@login_required
def member_update_view(request, pk):
    """
    Handles updating an existing member.
    """
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            success(request, f'Member {member.full_name} updated successfully!')
            return redirect('member_detail', pk=pk)
        else:
            for field, errors_list in form.errors.items():
                for err in errors_list:
                    error(request, f'{field}: {err}')
    else:
        form = MemberForm(instance=member)
    return render(request, 'church_finances/member_form.html', {'form': form, 'title': 'Update Member'})


# Tithing Management Views
@login_required
def tithing_list_view(request):
    """
    Displays a list of all tithing records with filtering options.
    """
    tithes = Tithing.objects.filter(is_active=True).select_related('member')
    filter_form = TithingFilterForm(request.GET or None)
    
    if filter_form.is_valid():
        member = filter_form.cleaned_data.get('member')
        year = filter_form.cleaned_data.get('year')
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        
        if member:
            tithes = tithes.filter(member=member)
        if year:
            tithes = tithes.filter(date__year=year)
        if start_date:
            tithes = tithes.filter(date__gte=start_date)
        if end_date:
            tithes = tithes.filter(date__lte=end_date)
    
    total_amount = tithes.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'tithes': tithes.order_by('-date'),
        'filter_form': filter_form,
        'total_amount': total_amount
    }
    return render(request, 'church_finances/tithing_list.html', context)


@login_required
def tithing_create_view(request):
    """
    Handles creation of new tithing records.
    """
    if request.method == 'POST':
        form = TithingForm(request.POST)
        if form.is_valid():
            tithing = form.save(commit=False)
            tithing.recorded_by = request.user
            tithing.save()
            success(request, f'Tithing record for {tithing.member.full_name} added successfully!')
            return redirect('tithing_list')
        else:
            for field, errors_list in form.errors.items():
                for err in errors_list:
                    error(request, f'{field}: {err}')
    else:
        form = TithingForm()
    return render(request, 'church_finances/tithing_form.html', {'form': form, 'title': 'Add New Tithing Record'})


@login_required
def tithing_update_view(request, pk):
    """
    Handles updating an existing tithing record.
    """
    tithing = get_object_or_404(Tithing, pk=pk)
    if request.method == 'POST':
        form = TithingForm(request.POST, instance=tithing)
        if form.is_valid():
            form.save()
            success(request, 'Tithing record updated successfully!')
            return redirect('tithing_list')
        else:
            for field, errors_list in form.errors.items():
                for err in errors_list:
                    error(request, f'{field}: {err}')
    else:
        form = TithingForm(instance=tithing)
    return render(request, 'church_finances/tithing_form.html', {'form': form, 'title': 'Update Tithing Record'})


@login_required
def tithing_delete_view(request, pk):
    """
    Handles deletion of a tithing record.
    """
    tithing = get_object_or_404(Tithing, pk=pk)
    if request.method == 'POST':
        tithing.is_active = False  # Soft delete
        tithing.save()
        success(request, 'Tithing record deleted successfully!')
        return redirect('tithing_list')
    return render(request, 'church_finances/confirm_delete_tithing.html', {'tithing': tithing})


# Printable Reports
@login_required
def member_tithing_report(request, pk):
    """
    Generate a printable tithing report for a specific member.
    """
    member = get_object_or_404(Member, pk=pk)
    year = request.GET.get('year')
    
    tithes = member.tithes.filter(is_active=True)
    if year:
        tithes = tithes.filter(date__year=year)
        report_title = f'Tithing Report for {member.full_name} - {year}'
    else:
        report_title = f'Complete Tithing Report for {member.full_name}'
    
    total_amount = tithes.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'member': member,
        'tithes': tithes.order_by('-date'),
        'total_amount': total_amount,
        'report_title': report_title,
        'year': year,
        'print_date': datetime.now().strftime('%B %d, %Y')
    }
    return render(request, 'church_finances/member_tithing_report.html', context)


@login_required
def annual_tithing_summary(request):
    """
    Generate an annual summary of all members' tithing.
    """
    year = request.GET.get('year', datetime.now().year)
    try:
        year = int(year)
    except (ValueError, TypeError):
        year = datetime.now().year
    
    members = Member.objects.filter(is_active=True)
    member_summaries = []
    
    for member in members:
        total = member.total_tithes(year)
        if total > 0:  # Only include members who tithed
            member_summaries.append({
                'member': member,
                'total': total
            })
    
    # Sort by total amount descending
    member_summaries.sort(key=lambda x: x['total'], reverse=True)
    
    grand_total = sum(summary['total'] for summary in member_summaries)
    
    context = {
        'year': year,
        'member_summaries': member_summaries,
        'grand_total': grand_total,
        'print_date': datetime.now().strftime('%B %d, %Y')
    }
    return render(request, 'church_finances/annual_tithing_summary.html', context)
