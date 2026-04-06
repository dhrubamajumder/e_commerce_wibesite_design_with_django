
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from django.views import View
from .models import Branch, Fund, ExpenseCategory, IncomeCategory, CustomerPayment, SupplierPayment, Customer
from .forms import BranchForm, FundForm, ExpenseCategoryForm, IncomeCategoryForm, CustomerPaymentForm, SupplierPaymentForm
from django.contrib import messages
from products.decorators import get_role_permissions, admin_required, staff_or_admin_required, get_role_permissions, role_permission_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from products.utils import paginate_queryset




# Create your views here.


# List all branches
class BranchListView(View):
    def get(self, request):
        branches = Branch.objects.all()
        return render(request, 'branch/branch_list.html', {'branches': branches})

# Create a new branch
class BranchCreateView(View):
    def get(self, request):
        form = BranchForm()
        return render(request, 'branch/branch_form.html', {'form': form})

    def post(self, request):
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Branch created successfully ✅")
            return redirect('branch_list')
        return render(request, 'branch/branch_form.html', {'form': form})

# Update branch
class BranchUpdateView(View):
    def get(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        form = BranchForm(instance=branch)
        return render(request, 'branch/branch_form.html', {'form': form})

    def post(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, "Branch updated successfully ✅")
            return redirect('branch_list')
        return render(request, 'branch/branch_form.html', {'form': form})

# Delete branch
class BranchDeleteView(View):
    def get(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        return render(request, 'branch/branch_confirm_delete.html', {'branch': branch})

    def post(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        branch.delete()
        return redirect('branch_list')
    
    
@login_required(login_url='/login/')
def fund_list(request):
    per_page = int(request.GET.get('per_page', 10))
    page = request.GET.get('page', 1)

    funds = Fund.objects.all().order_by('id')  # 👈 fresh queryset

    paginator = Paginator(funds, per_page)
    page_obj = paginator.get_page(page)
    role, permissions, permissions_list = get_role_permissions(request.user)


    return render(request, 'fund/fund_list.html', {
        'page_obj': page_obj,
        'per_page': per_page,
        'permissions':permissions,
        'permissions_list':permissions_list
    })
    

def fund_create(request):
    form = FundForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('fund_list')
    return render(request, 'fund/fund_form.html', {"form":form})

    
# def expense_category_list(request):
#     categories = ExpenseCategory.objects.all()
#     return render(request, 'expence/expence_list.html', {'categories': categories})
    
# def expense_category_create(request):
#     form = ExpenseCategoryForm(request.POST)
#     if form.is_valid():
#         form.save()
#         return redirect('expense_category_list')
#     return render(request, 'expence/expence_form.html', {'form':form})

def expense_category_view(request):
    # Get all categories and paginate
    categories = ExpenseCategory.objects.all().order_by('-id')
    page_obj = paginate_queryset(request, categories, per_page=10)
    # Get role and permissions for the current user
    role, permissions, permissions_list = get_role_permissions(request.user)
    form = ExpenseCategoryForm()
    if request.method == "POST":
        # Check if user has create permission
        if not request.user.is_superuser and 'expense_category_create' not in permissions_list:
            return render(request, '403.html', status=403)
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Expense category added successfully")
            return redirect('expense_category_list')
    context = {
        'form': form,
        'permissions': permissions,
        'permissions_list': permissions_list or [],
        'page_obj': page_obj,
        'per_page': request.GET.get('per_page', 10),
    }
    return render(request, 'expence/expense_category.html', context)


def expense_category_update(request, id):
    category = get_object_or_404(ExpenseCategory, id=id)
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            category.name = name
            category.save()
        return redirect("expense_category_list")
    return render(request, 'expence/expence_form.html', {'category':category})


def expense_category_delete(request, id):
    if request.method == "POST":
        ExpenseCategory.objects.filter(id=id).delete()
    return redirect('expense_category_list')


#  --------------------    income category  list   ----------------------
def income_category_list(request):
    categories = IncomeCategory.objects.all().order_by('-id')
    per_page = request.GET.get('per_page', 10)
    paginator = Paginator(categories, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    role, permissions, permissions_list = get_role_permissions(request.user)
    form = IncomeCategoryForm()
    if request.method == "POST":
        # Permission check
        if not request.user.is_superuser and 'other_income_category_create' not in permissions_list:
            return render(request, '403.html', status=403)
        form = IncomeCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Income category added successfully")
            return redirect('income_category_list')
    context = {
        'form': form,
        'permissions': permissions,
        'permissions_list': permissions_list or [],
        'page_obj': page_obj,
        'per_page': per_page,
    }
    return render(request, 'other_income/income_category.html', context)


@login_required(login_url='/login/')
def income_category_update(request, id):
    category = get_object_or_404(IncomeCategory, id=id)
    if request.method == "POST":
        category.name = request.POST.get("name")
        category.save()
    return redirect("income_category_list")


@login_required(login_url='/login/')
def income_category_delete(request, id):
    if request.method == "POST":
        IncomeCategory.objects.filter(id=id).delete()
    return redirect('income_category_list')


#----------------------------    Customer Payment List  ----------------
def customer_payment_list(request):
    customer = CustomerPayment.objects.all().order_by('-id')
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10
    paginator = Paginator(customer, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    role, permissions, permissions_list = get_role_permissions(request.user)
    context = {
        'permissions':permissions,
        'permissions_list':permissions_list,
        'page_obj': page_obj,
        'per_page': per_page,}
    return render(request, 'customer/payment_list.html', context)


@login_required(login_url='/login/')
def customer_payment_create(request):
    form = CustomerPaymentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('customer_payment_list')  
    customers = Customer.objects.all()
    funds = Fund.objects.all()
    context = {
        'form': form,
        'expense': None,
        'customers': customers,
        'funds': funds,}
    return render(request, 'customer/payment_form.html', context)


@login_required(login_url='/login/')
def customer_payment_update(request, id):
    payment = get_object_or_404(CustomerPayment, id=id)
    form = CustomerPaymentForm(request.POST or None, instance=payment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('customer_payment_list')
    customers = Customer.objects.all()
    funds = Fund.objects.all()
    context = {
        'form': form,
        'payment': payment,
        'customers': customers,
        'funds': funds,}
    return render(request, 'customer/payment_form.html', context)


# 4️⃣ Delete payment
@login_required(login_url='/login/')
def customer_payment_delete(request, id):
    expense = get_object_or_404(CustomerPayment, id=id)
    expense.delete()
    return redirect('customer_payment_list')