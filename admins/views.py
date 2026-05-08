
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from django.views import View
from .models import Branch, Fund, ExpenseCategory, IncomeCategory, CustomerPayment, SupplierPayment, Customer, FundTransfer, Supplier, Expense, OtherIncome, Slider, ClientReview
from .forms import BranchForm, FundForm, ExpenseCategoryForm, IncomeCategoryForm, CustomerPaymentForm, SupplierPaymentForm, FundTransferForm, ExpenseForm, OtherIncomeForm, SliderForm
from django.contrib import messages
from products.decorators import get_role_permissions, admin_required, staff_or_admin_required, get_role_permissions, role_permission_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from products.utils import paginate_queryset
from django.db import transaction




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
    
def user_slider_list(request):
    sliders = Slider.objects.all()
    return render(request, 'navbar/slider.html', {'sliders': sliders})
    
# def slider_list(request):
#     sliders = Slider.objects.all().order_by('-id')
#     return render(request, 'slider/slider_list.html', {'sliders': sliders})

def slider_list(request):
    sliders = Slider.objects.filter(status=True).order_by('-id')
    return render(request, 'slider/slider_list.html', {'sliders': sliders})

# Create Slider
def slider_create(request):
    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Slider created successfully!")
            return redirect('slider_list')
    else:
        form = SliderForm()

    return render(request, 'slider/slider_form.html', {'form': form})


# Update Slider
def slider_update(request, pk):
    slider = get_object_or_404(Slider, pk=pk)

    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES, instance=slider)
        if form.is_valid():
            form.save()
            messages.success(request, "Slider updated successfully!")
            return redirect('slider_list')
    else:
        form = SliderForm(instance=slider)

    return render(request, 'slider/slider_form.html', {'form': form, 'slider': slider})


# Delete Slider
def slider_delete(request, pk):
    slider = get_object_or_404(Slider, pk=pk)
    slider.delete()
    messages.success(request, "Slider deleted successfully!")
    return redirect('slider_list')


    
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


@login_required(login_url='/login/')
def fund_update(request, id):
    fund = get_object_or_404(Fund, id=id)
    form = FundForm(request.POST or None, instance=fund)
    if form.is_valid():
        form.save()
        return redirect('fund_list')
    return render(request, 'fund/fund_form.html', {'form': form, 'fund':fund})


# Delete
@login_required(login_url='/login/')
def fund_delete(request, id):
    fund = get_object_or_404(Fund, id=id)
    fund.delete()
    return redirect('fund_list')

    
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



#---------------------------  FUnd Transfer ------------------------

def fund_transfer_list(request):
    transfers = FundTransfer.objects.all().order_by('-id')
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10
    paginator = Paginator(transfers, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    role, permissions, permissions_list = get_role_permissions(request.user)
    context = {
        'permissions':permissions,
        'permissions_list':permissions_list,
        'page_obj': page_obj,
        'per_page': per_page,}
    return render(request, 'fund/fund_tran_list.html', context)


@login_required(login_url='/login/')
def fund_transfer_create(request):
    form = FundTransferForm(request.POST or None)
    funds = Fund.objects.filter(amount__gt=0)
    fund = Fund.objects.all()
    if request.method == 'POST' and form.is_valid():
        from_fund_id = request.POST.get('from_fund')
        to_fund_id = request.POST.get('to_fund')
        amount = form.cleaned_data['amount']
        date = form.cleaned_data['date']
        note = form.cleaned_data.get('note', '')
        # get Fund objects
        from_fund = get_object_or_404(Fund, pk=from_fund_id)
        to_fund = get_object_or_404(Fund, pk=to_fund_id)
        # Validate amount: can't transfer more than available
        if amount > from_fund.amount:
            messages.error(request, f"Cannot transfer {amount}. {from_fund.fund_name} only has {from_fund.amount}.")
            return redirect('fund_transfer_create')
        try:
            with transaction.atomic():
                # Create FundTransfer record
                transfer = FundTransfer.objects.create(
                    from_fund=from_fund,
                    to_fund=to_fund,
                    amount=amount,
                    date=date,
                    note=note,
                    created_by=request.user)
                # Update funds
                from_fund.amount -= amount
                from_fund.save()
                to_fund.amount += amount
                to_fund.save()
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('fund_transfer_create')
        messages.success(request, f"Transferred {amount} from {from_fund.fund_name} to {to_fund.fund_name}")
        return redirect('fund_transfer_list')
    context = {
        'form': form,
        'funds': funds,
        'fund': fund,
        'transfer': None,}
    return render(request, 'fund/fund_tran_form.html', context)



@login_required(login_url='/login/')
def fund_transfer_delete(request, id):
    transfer = get_object_or_404(FundTransfer, id=id)
    transfer.delete()
    return redirect('fund_transfer_list')

# ---------------   Supplier Payment list   ---------------------- 

def payment_list(request):
    supplier = SupplierPayment.objects.all().order_by('-id')
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10
    paginator = Paginator(supplier, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    role, permissions, permissions_list = get_role_permissions(request.user)
    context = {
        'permissions':permissions,
        'permissions_list':permissions_list,
        'page_obj': page_obj,
        'per_page': per_page,
        'supplier':supplier,}
    return render(request, 'supplier/payment_list.html', context)


@login_required(login_url='/login/')
def payment_create(request):
    form = SupplierPaymentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('supplier_payment_list')
    suppliers = Supplier.objects.all()
    funds = Fund.objects.all()
    context = {
        'form': form,
        'expense': None,
        'suppliers': suppliers,
        'funds': funds,}
    return render(request, 'supplier/payment_form.html', context)


@login_required(login_url='/login/')
def payment_update(request, id):
    expense = get_object_or_404(SupplierPayment, id=id)
    form = SupplierPaymentForm(request.POST or None, instance=expense)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('supplier_payment_list')
    suppliers = Supplier.objects.all()
    funds = Fund.objects.all()
    context = {
        'form': form,
        'expense': expense,
        'suppliers': suppliers,
        'funds': funds,}
    return render(request, 'supplier/payment_form.html', context)


# 4️⃣ Delete payment
@login_required(login_url='/login/')
def payment_delete(request, id):
    expense = get_object_or_404(SupplierPayment, id=id)
    expense.delete()
    return redirect('supplier_payment_list')




# ===========================   Expence Create  ===========================

@login_required(login_url='/login/')
def expense_list(request):
    expenses = Expense.objects.all().order_by('-id')
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10
    paginator = Paginator(expenses, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    role, permissions, permissions_list = get_role_permissions(request.user)

    context = {
        'page_obj': page_obj,
        'per_page': per_page,
        'permissions':permissions,
        'permissions_list':permissions_list,
        }
    return render(request, 'expence/expence_list.html', context)


# 2️⃣ Create Expense
@login_required(login_url='/login/')
def expense_create(request):
    form = ExpenseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('expense_list')
    categories = ExpenseCategory.objects.all()
    funds = Fund.objects.all()
    context = {
        'form': form,
        'expense': None,
        'categories': categories,
        'funds': funds,}
    return render(request, 'expence/expence_form.html', context)


# Update Expense
@login_required(login_url='/login/')
def expense_update(request, id):
    expense = get_object_or_404(Expense, id=id)
    form = ExpenseForm(request.POST or None, instance=expense)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('expense_list')
    categories = ExpenseCategory.objects.all()
    funds = Fund.objects.all()
    context = {
        'form': form,
        'expense': expense,
        'categories': categories,
        'funds': funds,}
    return render(request, 'expence/expence_form.html', context)

# 4️⃣ Delete Expense
@login_required(login_url='/login/')
def expense_delete(request, id):
    expense = get_object_or_404(Expense, id=id)
    expense.delete()
    return redirect('expense_list')




# -=====================================================   Other Income List  ===========================================
@login_required(login_url='/login/')
def other_income_list(request):
    income = OtherIncome.objects.all().order_by('-id')
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10
    paginator = Paginator(income, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    role, permissions, permissions_list = get_role_permissions(request.user)
    context = {
        'permissions':permissions,
        'permissions_list':permissions_list,
        'page_obj': page_obj,
        'per_page': per_page,}
    return render(request, 'other_income/income_list.html', context)


@login_required(login_url='/login/')
def other_income_create(request):
    form = OtherIncomeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('other_income_list')
    categories = IncomeCategory.objects.all()
    funds = Fund.objects.all()
    context = {
        'form': form,
        'expense': None,
        'categories': categories,
        'funds': funds,}
    return render(request, 'other_income/income_form.html', context)

# Update income
@login_required(login_url='/login/')
def other_income_update(request, id):
    expense = get_object_or_404(OtherIncome, id=id)
    form = OtherIncomeForm(request.POST or None, instance=expense)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('other_income_list')
    categories = IncomeCategory.objects.all()
    funds = Fund.objects.all()
    context = {
        'form': form,
        'expense': expense,
        'categories': categories,
        'funds': funds,}
    return render(request, 'other_income/income_form.html', context)


# 4️⃣ Delete Expense
@login_required(login_url='/login/')
def other_income_delete(request, id):
    expense = get_object_or_404(OtherIncome, id=id)
    expense.delete()
    return redirect('other_income_list')



# ---------------------------------   Client Reviews List   --------------------------- 
def client_review_list(request):
    reviews = ClientReview.objects.all()
    return render(request, 'client/client_review_list.html', {'reviews': reviews})

# Create + Update
def client_review_create_update(request, id=None):
    review = None
    if id:
        review = get_object_or_404(ClientReview, id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        designation = request.POST.get('designation')
        review_text = request.POST.get('review')
        rating = request.POST.get('rating')
        status = True if request.POST.get('status') == '1' else False

        if review:
            review.name = name
            review.designation = designation
            review.review = review_text
            review.rating = rating
            review.status = status
            if request.FILES.get('photo'):
                review.photo = request.FILES.get('photo')
            review.save()
            messages.success(request, "Client review updated successfully!")
        else:
            ClientReview.objects.create(
                name=name,
                designation=designation,
                review=review_text,
                rating=rating,
                status=status,
                photo=request.FILES.get('photo')
            )
            messages.success(request, "Client review created successfully!")
        return redirect('client_review_list')
    return render(request, 'client/client_form.html', {'review': review})


# Delete
def client_review_delete(request, id):
    review = get_object_or_404(ClientReview, id=id)
    review.delete()
    messages.success(request, "Client review deleted successfully!")
    return redirect('client_review_list')





