from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . models import Category, Product, Cart, Order, CartItem, OrderItem, Wishlist, Supplier, Customer, SystemSettings, Purchase, PurchaseItem, Stock, Profile
from . forms import ProductForm, SystemSettingsForm, CustomerForm, PurchaseForm, PurchaseItemForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Product
import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import modelformset_factory
from django.db.models import Sum , F
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction


def dashboard_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            return redirect('product_list')
    return redirect('login')


@login_required
def user_dashboard(request):
    return render(request, 'product/product_list.html')


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')




@login_required
@user_passes_test(lambda u: u.is_staff)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category/category_list.html', {'categories': categories})

@login_required
@user_passes_test(lambda u: u.is_staff)
def category_create(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        Category.objects.create(name=name, description=description)
        messages.success(request, "Category created successfully ✅")
        return redirect('category_list')
    return render(request, 'category/category_form.html')


def topbar_list(request, category_id=None):
    categorys = Category.objects.all()
    if category_id:
        products = Product.objects.filter(category_id=category_id).order_by('-id')
    else:
        products = Product.objects.all().order_by('-id')
    context = {
        'products':products,
        'categorys':categorys,
        'selected_category':category_id
    }
    return render(request, 'navbar/topbar.html', context)

# -------------------------------------------   Product Views  -------------------------------------

def product_list(request, category_id=None):
    categorys = Category.objects.all()
    search_query = request.GET.get('q')  
    products = Product.objects.filter(stock__quantity__gt=0)  # ✅ Only products with stock
    # Category filter
    if category_id:
        products = products.filter(category_id=category_id)
    # Search filter
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    products = products.order_by('-id')
    # Wishlist products (only if logged in)
    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)
    context = {
        'products': products,
        'categorys': categorys,
        'selected_category': category_id,
        'wishlist_products': wishlist_products,
        'search_query': search_query  
    }
    return render(request, 'product/product_list.html', context)


def stock_lists(request):
    stocks = Stock.objects.select_related('product').all()
    context = {'stocks': stocks}
    return render(request, 'stock/product_stock_list.html', context)


def stock_list(request):
    stocks = Stock.objects.select_related('product', 'product__category')
    stock_data = []
    for stock in stocks:
        supplier_info = (
            PurchaseItem.objects
            .filter(product=stock.product, purchase__status="Received")
            .values('purchase__supplier__name')
            .annotate(total_qty=Sum('quantity'))
        )
        stock_data.append({
            'stock': stock,
            'suppliers': supplier_info
        })
    context = {
        'stock_data': stock_data
    }
    return render(request, 'stock/stock_list.html', context)


def ajax_search(request):
    query = request.GET.get('q')
    products = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )[:10]

        for product in results:
            products.append({
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'image': product.image.url if product.image else ''
            })

    return JsonResponse({'products': products})



@login_required
@user_passes_test(lambda u: u.is_staff)
def product(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'product/product.html', {'products':products})
    
@login_required
@user_passes_test(lambda u: u.is_staff)
def product_create(request):
    categories = Category.objects.all()
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        print('hello')
        if form.is_valid():
            form.save()
            print('save')
            messages.success(request, "Product added successfully ✅")
            return redirect('product_list')
        else:
            print(form.errors)   # 👈 ADD THIS
    else:
        form = ProductForm()
    context = {'form': form, 'categories': categories}
    return render(request, 'product/product_form.html', context)


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    related_products = Product.objects.filter(
        category_id=product.category_id
    ).exclude(id=product.id).order_by('-id')[:4]
    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'product/product_view.html', context)


def content(request):
    return render(request, 'navbar/content.html')


# --------------------------------------------------------------------------------------
# -----------------------------     Cart      ------------------------------------------
# --------------------------------------------------------------------------------------

def update_cart(request):
    if request.method != "POST":
        return JsonResponse({"status": "fail"})

    data = json.loads(request.body)
    item_id = data.get("item_id")
    action = data.get("action")

    # ================= Login user =================
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).order_by('-created_at').first()
        if not cart:
            cart = Cart.objects.create(user=request.user)

        try:
            cart_item = CartItem.objects.get(id=item_id)
            cart = cart_item.cart
        except CartItem.DoesNotExist:
            return JsonResponse({"status": "fail", "message": "Cart item not found"}, status=404)

        if action == "inc":
            cart_item.quantity += 1
            cart_item.save()
        elif action == "dec":
            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                cart_item.delete()
                return JsonResponse({
                    "status": "success",
                    "quantity": 0,
                    "cart_count": cart.items.count(),
                    "cart_total": float(cart.get_total_price())
                })
            cart_item.save()

        return JsonResponse({
            "status": "success",
            "quantity": cart_item.quantity,
            "subtotal": float(cart_item.total_price()),
            "cart_count": cart.items.count(),
            "cart_total": float(cart.get_total_price())
        })

    # ================= Guest user (Session) =================
    else:
        cart = request.session.get("cart", {})

        if action == "inc":
            cart[item_id] = cart.get(item_id, 0) + 1
        elif action == "dec":
            if item_id in cart:
                cart[item_id] -= 1
                if cart[item_id] <= 0:
                    del cart[item_id]

        request.session["cart"] = cart
        request.session.modified = True

        # subtotal & cart_total হিসাব
        try:
            product = Product.objects.get(id=item_id)
        except Product.DoesNotExist:
            return JsonResponse({"status": "fail", "message": "Product not found"}, status=404)

        quantity = cart.get(item_id, 0)
        subtotal = product.product_price * quantity
        cart_total = sum(Product.objects.get(id=pid).product_price * qty for pid, qty in cart.items())

        return JsonResponse({
            "status": "success",
            "quantity": quantity,
            "subtotal": float(subtotal),
            "cart_count": sum(cart.values()),
            "cart_total": float(cart_total)
        })

def remove_item(request, pk):
    # Logged in
    if request.user.is_authenticated:
        item = CartItem.objects.filter(
            id=pk,
            cart__user=request.user
        ).first()
        if item:
            cart = item.cart
            item.delete()
            return JsonResponse({
                "status": "success",
                "cart_count": cart.items.count(),
                "cart_total": float(cart.get_total_price())
            })
    # Guest
    else:
        cart = request.session.get('cart', {})
        product_id = str(pk)
        if product_id in cart:
            del cart[product_id]
        request.session['cart'] = cart
        request.session.modified = True
        total = 0
        for pid, qty in cart.items():
            p = Product.objects.get(id=pid)
            total += p.product_price * qty
        return JsonResponse({
            "status": "success",
            "cart_count": sum(cart.values()),
            "cart_total": float(total)
        })
    return JsonResponse({"status": "fail"})



def add_to_cart(request, pk):
    product = get_object_or_404(Product, id=pk)
    # ---------------- LOGGED IN USER ----------------
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        quantity = cart_item.quantity
        subtotal = cart_item.total_price()
        cart_count = cart.items.count()
        cart_total = cart.get_total_price()
        item_id = cart_item.id   # DB item id

    # ---------------- GUEST USER ----------------
    else:
        cart = request.session.get('cart', {})
        product_id = str(pk)
        if product_id in cart:
            cart[product_id] += 1
        else:
            cart[product_id] = 1
        request.session['cart'] = cart
        request.session.modified = True
        quantity = cart[product_id]
        subtotal = product.product_price * quantity
        cart_count = sum(cart.values())
        cart_total = 0
        for pid, qty in cart.items():
            p = Product.objects.get(id=pid)
            cart_total += p.product_price * qty
        item_id = product.id  
    return JsonResponse({
        "id": item_id,
        "name": product.name,
        "price": float(product.product_price),
        "image": product.image.url if product.image else "",
        "quantity": quantity,
        "subtotal": float(subtotal),
        "cart_count": cart_count,
        "cart_total": float(cart_total),
    })
    
    
def get_cart_items(request):
    items = []
    cart_total = 0
    cart_count = 0

    # 🔹 Logged in user
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            cart_items = CartItem.objects.filter(cart=cart)

            for item in cart_items:
                subtotal = item.total_price()
                cart_total += subtotal
                cart_count += item.quantity

                items.append({
                    "id": item.id,  # CartItem id
                    "name": item.product.name,
                    "price": float(item.product.product_price),
                    "image": item.product.image.url if item.product.image else "",
                    "quantity": item.quantity,
                    "subtotal": float(subtotal)
                })

    # 🔹 Guest user (session cart)
    else:
        cart = request.session.get('cart', {})

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)

            subtotal = product.product_price * quantity
            cart_total += subtotal
            cart_count += quantity

            items.append({
                "id": product.id,
                "name": product.name,
                "price": float(product.product_price),
                "image": product.image.url if product.image else "",
                "quantity": quantity,
                "subtotal": float(subtotal)
            })

    return JsonResponse({
        "items": items,
        "cart_total": float(cart_total),
        "cart_count": cart_count
    })
            


def cart_items_json(request):
    cart_items = Cart.objects.filter(user=request.user)
    items = []
    grand_total = 0
    for item in cart_items:
        subtotal = item.total_price()
        grand_total += subtotal
        items.append({
            "id": item.id,
            "name": item.product.name,
            "qty": item.quantity,
            "price": float(item.product.product_price),
            "subtotal": float(subtotal)
        })
    return JsonResponse({
        "items": items,
        "grand_total": grand_total
    })
    
def cart_json(request):
    if request.user.is_authenticated:
        cart = request.user.carts.order_by('-created_at').first()  # latest cart
        items = []
        grand_total = 0

        if cart:
            for item in cart.items.all():  # related_name="items" from CartItem
                subtotal = item.total_price()
                grand_total += subtotal
                items.append({
                    "id": item.id,
                    "name": item.product.name,
                    "qty": item.quantity,
                    "price": float(item.product.product_price),
                    "subtotal": float(subtotal)
                })

        return JsonResponse({
            "items": items,
            "grand_total": float(grand_total)
        })
    else:
        # Guest session cart
        cart = request.session.get('cart', {})
        items = []
        grand_total = 0
        for product_id, qty in cart.items():
            product = Product.objects.get(id=product_id)
            subtotal = product.product_price * qty
            grand_total += subtotal
            items.append({
                "id": product.id,
                "name": product.name,
                "qty": qty,
                "price": float(product.product_price),
                "subtotal": float(subtotal)
            })
        return JsonResponse({
            "items": items,
            "grand_total": float(grand_total)
        })


def cart_list(request):
    if not request.user.is_authenticated:
        return render(request, "auths/login_required_message.html")

    cart_items = CartItem.objects.filter(cart__user=request.user)
    total = sum(item.total_price() for item in cart_items)

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        delivery_date = request.POST.get("delivery_date")
        payment = request.POST.get("payment")

        if not cart_items.exists():
            messages.warning(request, "Your cart is empty!")
            return redirect("cart_list")

        order = Order.objects.create(
            user=request.user,
            phone=phone,
            address=address,
            delivery_date=delivery_date,
            payment_method=payment,
            total_amount=total
        )

        order_items = []
        for item in cart_items:
            order_items.append(OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.product_price
            ))
        OrderItem.objects.bulk_create(order_items)

        cart_items.delete()

        messages.success(request, "Order placed successfully!")
        return redirect("user_order_list")

    return render(request, "cart_list.html", {
        "cart_items": cart_items,
        "total": total
    })

# def cart_details_list(request):
#     orders = Order.objects.filter(user=request.user).order_by('id')
#     return render(request, "product/cart_details_list.html", {"orders": orders})

@login_required
def user_order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, "product/user_order_list.html", {"orders": orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != 'Cancelled':
        order.status = 'Cancelled'
        order.save()  # Stock will be restored if Shipped
        messages.success(request, "Order canceled successfully.")
    else:
        order.status = 'Pending'
        order.save()  # Undo cancel, stock logic handled in save()
        messages.success(request, "Order restored successfully.")
    return redirect('user_order_list')


@login_required
def admin_order_list(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed here")
    orders = Order.objects.exclude(status='canceled').order_by('-id')
    return render(request, 'admin/order_list.html', {'orders': orders})


@login_required
@require_POST
def update_order_status(request, order_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    if order.status == 'Shipped':
        return JsonResponse({
            'error': 'Order already shipped. Status cannot be changed.'
        }, status=400)

    if new_status not in dict(Order.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    # ==============================
    #      STOCK CHECK BEFORE SHIPPED
    # ==============================
    if new_status == 'Shipped':
        for item in order.items.select_related('product__stock'):
            stock = item.product.stock
            if stock.quantity < item.quantity:
                return JsonResponse({
                    'error': f"Not enough stock for {item.product.name}"
                }, status=400)
        with transaction.atomic():
            for item in order.items.select_related('product__stock'):
                item.product.stock.quantity = F('quantity') - item.quantity
                item.product.stock.save()
            order.status = 'Shipped'
            order.save()
        return JsonResponse({
            'success': True,
            'status': order.status
        })
    # ==============================
    # NORMAL STATUS UPDATE
    # ==============================
    order.status = new_status
    order.save()
    return JsonResponse({
        'success': True,
        'status': order.status
    })
    

@login_required
def offcanvas(request):
    return render(request, 'product/offcanvas.html')



def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
    else:
        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
        wishlist_item, created = Wishlist.objects.get_or_create(
            session_key=request.session.session_key,
            product=product
        )
    if not created:
        wishlist_item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


def wishlist_view(request):

    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()

        wishlist_items = Wishlist.objects.filter(
            session_key=request.session.session_key
        )

    return render(
        request,
        "wish/wishlist.html",
        {"wishlist_items": wishlist_items}
    )


def wish(request):
    products = Product.objects.all()
    return render(request, 'wish/wish.html', {'products':products})


# --------------------------------------------  Footer  -------------------------------

def about(request):
    return render(request, 'navbar/about.html')

def contact(request):
    return render(request, 'navbar/contact.html')

def faq(request):
    return render(request, 'navbar/faq.html')

# --------------------------------------------  Profile  --------------------------------
@login_required
def profile_list(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'navbar/profile_list.html', {'profile': profile})

def profile_update(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        if request.FILES.get('image'):
            profile.image = request.FILES.get('image')
        profile.save()
        messages.success(request, "Profile updated successfully ✅")
        return redirect('profile_list')  
    return render(request, 'navbar/profile_update.html', {'profile': profile})



@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        if request.FILES.get('image'):
            profile.image = request.FILES.get('image')
        profile.save()
        return redirect('admin_profile')  
    return render(request, 'admin/profile.html', {'profile': profile})


def demo(request):
    return render(request, 'demo.html')




# ------------------------------------------------------------
# --------------        Supplier Views        -------------
# ------------------------------------------------------------


def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('-id')
    per_page = request.GET.get('per_page', 10)
    paginator = Paginator(suppliers, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'per_page': per_page,
        }
    return render(request, 'supplier/suppliers.html', context)


# -----------------------------
# Supplier Create View
# -----------------------------

def supplier_create(request):
    if request.method == "POST":
        Supplier.objects.create(
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
        )
        messages.success(request, "✅ Supplier added successfully")
        return redirect('supplier')
    return render(request, 'supplier/supplier_form.html')


def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == "POST":
        supplier.name = request.POST.get('name')
        supplier.phone = request.POST.get('phone')
        supplier.address = request.POST.get('address')
        supplier.save()
        messages.success(request, "Supplier updated successfully")
        return redirect('supplier')
    context = {'supplier': supplier}
    return render(request, 'supplier/supplier_form.html', context)

# -----------------------------
# Supplier Delete View
# -----------------------------
@login_required(login_url='/login/')
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.delete()
        messages.success(request, "🗑️ Supplier deleted successfully")
    return redirect('supplier')



# ------------------------------------------------------------
# --------------        Supplier Views        ----------------
# ------------------------------------------------------------

@login_required(login_url='/login/')
def settings_list(request):
    settings_instance = SystemSettings.objects.first()
    return render(request, 'settings/setting_list.html', {'settings': settings_instance})


# Create new system settings
@login_required(login_url='/login/')
def setting_create(request):
    if SystemSettings.objects.exists():
        return redirect('settings_list')
    if request.method == "POST":
        form = SystemSettingsForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            if request.POST.get('delete_logo') and instance.logo:
                instance.logo.delete(save=False)
                instance.logo = None
            instance.save()
            messages.success(request, "System settings created successfully ✅")
            return redirect('settings_list')
    else:
        form = SystemSettingsForm()
    print(form.instance.logo)   
    print(form.errors)    
    return render(request, 'settings/setting_form.html', {'form': form, 'title': 'Create System Settings'})
      

@login_required(login_url='/login/')
def setting_update(request, pk):
    settings_update = get_object_or_404(SystemSettings, pk=pk)

    if request.method == "POST":
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings_update)  # ✅ instance যোগ করা হয়েছে
        if form.is_valid():
            instance = form.save(commit=False)
            if request.POST.get('delete_logo') and instance.logo:
                instance.logo.delete(save=False)
                instance.logo = None

            instance.save()
            messages.success(request, "System settings updated successfully ✅")
            return redirect('settings_list')
    else:
        form = SystemSettingsForm(instance=settings_update)
    return render(request, 'settings/setting_form.html', {
        'form': form,
        'title': 'Update System Settings'
    })



# --------------------------------------------------------------  Customer View -----------------------------------------------------------

@login_required(login_url='/login/')
def customer_list(request):
    customers = Customer.objects.all().order_by('-id')
    return render(request, 'customer/customer.html', {'customers': customers})  

# ---------------------------
# 2. Customer Create View
# ---------------------------

@login_required(login_url='/login/')
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Customer added successfully")
            return redirect('customer')
    else:
        form = CustomerForm()
    return render(request, 'customer/customer_form.html', {'form': form})


# ---------------------------
# 3. Customer Update View
# ---------------------------

@login_required(login_url='/login/')
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Customer updated successfully")
            return redirect('customer')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer/customer_form.html', {'form': form, 'customer': customer})


# ---------------------------
# 4. Customer Delete View
# ---------------------------

@login_required(login_url='/login/')
def customer_delete(request, pk):
    if request.method == "POST":
        Customer.objects.filter(pk=pk).delete()
        messages.success(request, "🗑️ Customer deleted successfully")
    return redirect('customer')



# ================= Purchase List =================
@login_required
def purchase_list(request):
    purchases = Purchase.objects.all().order_by('-id')
    return render(request, 'purchase/purchase_list.html', {'purchases': purchases})


# ================= Purchase Create =================
# @login_required
# def purchase_create(request):
#     # ModelFormset for PurchaseItem
#     PurchaseItemFormSet = modelformset_factory(
#         PurchaseItem,
#         form=PurchaseItemForm,
#         extra=1,
#         can_delete=True
#     )

#     if request.method == "POST":
#         purchase_form = PurchaseForm(request.POST)
#         formset = PurchaseItemFormSet(request.POST, queryset=PurchaseItem.objects.none())

#         if purchase_form.is_valid() and formset.is_valid():
#             # Save Purchase
#             purchase = purchase_form.save(commit=False)
#             purchase.created_by = request.user
#             purchase.save()

#             # Save PurchaseItems
#             for form in formset:
#                 if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
#                     item = form.save(commit=False)
#                     item.purchase = purchase
#                     item.save()

#             # Update total_amount based on items
#             purchase.update_total_amount()

#             messages.success(request, "Purchase created successfully!")
#             return redirect('purchase_list')

#     else:
#         purchase_form = PurchaseForm()
#         formset = PurchaseItemFormSet(queryset=PurchaseItem.objects.none())

#     return render(request, 'purchase/purchase_form.html', {
#         'purchase_form': purchase_form,
#         'formset': formset,
#         'is_update': False,
#     })



def purchase_create(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        items_json = request.POST.get('purchase_items')
        if form.is_valid() and items_json:
            purchase = form.save(commit=False)
            purchase.created_by = request.user
            purchase.save()
            items = json.loads(items_json)
            for item in items:
                product = Product.objects.get(pk=item['product_id'])
                # Create PurchaseItem
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    quantity=item['quantity'],
                    purchase_price=item['price']
                )
                # Update Stock
                stock, created = Stock.objects.get_or_create(product=product)
                stock.quantity += item['quantity']
                stock.save()
            # Update purchase total
            purchase.update_total_amount()
            messages.success(request, "Purchase created successfully!")
            return redirect('purchase_list')
        else:
            # Show validation errors
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            if not items_json:
                messages.error(request, "No items were added to the purchase.")
    else:
        form = PurchaseForm()

    context = {
        'form': form,
        'purchase': None,
        'suppliers': Supplier.objects.all(),
        'categories': Category.objects.all(),
        'products': Product.objects.all(),
    }
    return render(request, 'purchase/purchase_form.html', context)
