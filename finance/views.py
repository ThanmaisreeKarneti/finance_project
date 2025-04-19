from decimal import Decimal
from unicodedata import category
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from finance.forms import IncomeForm
from collections import defaultdict
from .forms import AccountSettingsForm, CategoryForm, TransactionForm
from .models import  Income,  Transaction, Wallet, Category
from django.db.models import Sum
from datetime import date, datetime, timedelta 
import calendar
import json
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now 
from django.db.models.functions import TruncMonth,Lower
from django.contrib.auth.hashers import make_password
from .forms import SignUpForm


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Signup failed. Please fix the errors below.")
    else:
        form = SignUpForm()
    return render(request, 'finance/signup.html', {'form': form})


def login_page(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        print("EMAIL:", email)
        print("PASSWORD:", password)

        user = authenticate(request, username=email, password=password)
        print("USER:", user)

        if user is not None:
            login(request, user)
            print("LOGIN SUCCESSFUL ✅")
            return redirect('dashboard')
        else:
            print("LOGIN FAILED ❌")
            messages.error(request, "Invalid email or password.")
    
    return render(request, 'finance/login.html')


@login_required(login_url='/')
def dashboard(request):
    return render(request, 'finance/dashboard.html')

@login_required
def wallet(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    return render(request, 'finance/wallet.html', {'wallet': wallet})


def edit_balance(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        new_balance = request.POST.get('balance')
        wallet.balance = new_balance
        wallet.save()
        return redirect('wallet')

    return render(request, 'finance/edit_balance.html', {'wallet': wallet})


def add_income(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        date = request.POST['date']
        Transaction.objects.create(
            user=request.user,
            amount=amount,
            date=date,
            type='income'  # THIS LINE IS VERY IMPORTANT
        )
        return redirect('wallet')
        if amount:
            amount = int(amount)
            

            # Update wallet balance
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += amount
            wallet.save()

            return redirect('wallet')
    

    return render(request, 'finance/add_income.html')


@login_required
def add_expense(request):
    categories = Category.objects.all()
    user_wallet = Wallet.objects.get(user=request.user)
    balance = user_wallet.balance

    low_balance_threshold = 500  # Alert if expense is less than ₹500

    if request.method == "POST":
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        category_id = request.POST.get('category')

        # If amount is less than ₹500, show message and redirect to notifications
        if balance < low_balance_threshold:
            messages.warning(request, "❌ No more expenses allowed. Wallet balance is below ₹500.")
            return redirect('notifications') # Redirect to notifications page

        # If amount is valid (greater than ₹500), continue processing the expense
        if category_id:
            try:
                category = Category.objects.get(id=category_id)  # Fetch category

                # Check if amount, date, and category are valid
                if amount and date and category:
                    # Create expense transaction
                    transaction = Transaction.objects.create(
                        user=request.user,
                        amount=amount,
                        date=date,
                        category=category,
                        type='expense'
                    )

                    # Subtract amount from wallet
                    user_wallet.balance -= int(amount)
                    user_wallet.save()

                    messages.success(request, f"✅ Expense of ₹{amount} added successfully.")
                    return redirect('overview')  # Redirect to the overview page

                else:
                    return render(request, 'finance/add_expense.html', {
                        'error_message': "Please provide valid data for amount, date, and category.",
                        'categories': categories
                    })

            except Category.DoesNotExist:
                return render(request, 'finance/add_expense.html', {
                    'error_message': "Invalid category selected.",
                    'categories': categories
                })
        else:
            return render(request, 'finance/add_expense.html', {
                'error_message': "Please select a category.",
                'categories': categories
            })

    return render(request, 'finance/add_expense.html', {
        'categories': categories
    })


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_category')
    else:
        form = CategoryForm()
    if 'category_name' in request.POST:
        Category.objects.create(name=request.POST['category_name'])

    

    categories = Category.objects.all()
    return render(request, 'finance/add_category.html', {
        'form': form,
        'categories': categories
    })


def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        # Delete related transactions manually
        Transaction.objects.filter(category=category).delete()
        category.delete()
        return redirect('add_category')

    return redirect('add_category')




def add_transaction(request):
    form = TransactionForm()
    categories = Category.objects.all()  # Fetch all categories
    return render(request, 'finance/your_template.html', {'form': form, 'categories': categories})


@login_required
def settings_view(request):
    user = request.user

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Update name and email
        full_name = name.strip().split(" ", 1)
        first_name = full_name[0]
        last_name = full_name[1] if len(full_name) > 1 else ''
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        # Generate a username from the name
        base_username = f"{first_name}{last_name}".replace(" ", "")
        new_username = base_username
        counter = 1
        # Ensure uniqueness of username (excluding current user)
        while User.objects.exclude(pk=user.pk).filter(username=new_username).exists():
            new_username = f"{base_username}{counter}"
            counter += 1
        user.username = new_username

        # Only update password if both fields are filled and match
        if password and confirm_password:
            if password == confirm_password:
                user.password = make_password(password)
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Passwords do not match.")
                return redirect('settings')

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('settings')

    return render(request, 'finance/settings.html',{
        'username':request.user.username
    })

@login_required
def notifications(request):
    return render(request, 'finance/notifications.html', {
        'messages': messages.get_messages(request)
    })

@login_required
def overview(request):
    transactions = Transaction.objects.filter(user=request.user, type='expense')
    expense_summary = defaultdict(float)

    for txn in transactions:
        if txn.category_id:
            expense_summary[txn.category.name] += float(txn.amount)


    # Get chart data (same logic as in profit_loss view)
    user = request.user
    # Current Wallet Balance
    wallet = Wallet.objects.filter(user=user).first()
    balance = wallet.balance if wallet else 0
    # Total Income and Expense
    income_total = Transaction.objects.filter(user=user, type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = Transaction.objects.filter(user=user, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    total_spent = expense_total


    # Bar Chart: Monthly Expenses
    from django.db.models.functions import TruncMonth
    monthly_expenses = (
        Transaction.objects
        .filter(user=user, type='expense')
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    bar_labels = [entry['month'].strftime('%b %Y') for entry in monthly_expenses]
    bar_data = [float(entry['total']) for entry in monthly_expenses]

    # Pie Chart: Income vs Expense
    pie_labels = ["Income", "Expense"]
    pie_data = [float(balance), float(total_spent)]

    # Monthly spent (Total for the last  months)
    months_with_data = Transaction.objects.filter(
        user=user,
        type = 'expense'
        ).annotate(month=TruncMonth('date')).values('month').annotate(
            total=Sum('amount')
        ).order_by('-month')[:4]
    

    months_with_data = reversed(months_with_data)
    
    line_labels = []
    line_data = []

    # Loop through the last  months
    for entry in months_with_data:
        month_start = entry['month']
        next_month = (month_start + relativedelta(months=1))

        total_expense = Transaction.objects.filter(
            user=user,
            type='expense',
            date__gte=month_start,
            date__lt=next_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Convert the total_expense to integer
        line_labels.append(month_start.strftime('%b %Y'))
        line_data.append(int(total_expense))  # Convert total_expense to integer 
    # Pass data to the template
    context = {
        'expense_summary': dict(expense_summary),  # Pass the expense summary data
        'bar_labels': json.dumps(bar_labels),  # Bar chart data
        'bar_data': json.dumps(bar_data),  # Bar chart data
        'pie_labels': json.dumps(pie_labels),  # Pie chart labels
        'pie_data': json.dumps(pie_data),  # Pie chart data
        'line_labels': json.dumps(line_labels),  # Line chart labels
        'line_data': json.dumps(line_data),  # Line chart data
    }

    return render(request, 'finance/overview.html', context)


@login_required
def recent_activities(request):
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date')
    
    return render(request, 'finance/recent_activities.html', {
        'transactions': transactions
    })



@login_required
def profit_loss(request):
    user = request.user

    # Wallet balance
    wallet = Wallet.objects.filter(user=user).first()
    balance = wallet.balance if wallet else 0



    # Income and expense totals
    income_total = Transaction.objects.filter(user=user, type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = Transaction.objects.filter(user=user, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    total_spent = expense_total
    profit_amount = income_total - expense_total

    # Percentages
    initial = balance + total_spent
    profit_percentage = round((balance / initial) * 100, 2) 
    expense_percentage = round((total_spent / initial) * 100, 2) 

    # Monthly spent
    now = datetime.now()

    monthly_spent = Transaction.objects.annotate(
        type_lower=Lower('type')).filter(
        user=request.user,
        type_lower='expense',
        date__month=now.month,
        date__year=now.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Bar Chart: Monthly expenses
    monthly_expenses = (
        Transaction.objects
        .filter(user=user, type='expense')
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    bar_labels = [entry['month'].strftime('%b %Y') for entry in monthly_expenses]
    bar_data = [float(entry['total']) for entry in monthly_expenses]

    # Pie Chart: Income vs Expense
    pie_labels = ["Income", "Expense"]
    pie_data = [float(balance), float(total_spent)]

   # Monthly spent (Total for the last  months)
    months_with_data = Transaction.objects.filter(
        user=user,
        type = 'expense'
        ).annotate(month=TruncMonth('date')).values('month').annotate(
            total=Sum('amount')
        ).order_by('-month')[:4]
    

    months_with_data = reversed(months_with_data)
    
    line_labels = []
    line_data = []

    # Loop through the last  months
    for entry in months_with_data:
        month_start = entry['month']
        next_month = (month_start + relativedelta(months=1))

        total_expense = Transaction.objects.filter(
            user=user,
            type='expense',
            date__gte=month_start,
            date__lt=next_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Convert the total_expense to integer
        line_labels.append(month_start.strftime('%b %Y'))
        line_data.append(int(total_expense))  # Convert total_expense to integer 

    context = {
        'monthly_spent': monthly_spent,
        'total_spent': total_spent,
        'balance': balance,
        'bar_labels': json.dumps(bar_labels),
        'bar_data': json.dumps(bar_data),
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'line_labels': json.dumps(line_labels),
        'line_data': json.dumps(line_data),
        'profit_percentage': profit_percentage,
        'loss_percentage': expense_percentage,
    }

    return render(request, 'finance/profit_loss.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')
