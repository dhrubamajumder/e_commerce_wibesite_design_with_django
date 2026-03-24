from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . models import Category, Product, Cart, Order, CartItem, OrderItem, Wishlist
from . forms import ProductForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Product
import json
from django.db.models import Q

# Create your views here.

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category/category_list.html', {'categories': categories})

def category_create(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        Category.objects.create(name=name, description=description)
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
    products = Product.objects.all()
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
    # ✅ Wishlist products (only if logged in)
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




def product(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'product/product.html', {'products':products})
    

def product_create(request):
    categories = Category.objects.all()
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        print('hello')
        if form.is_valid():
            form.save()
            print('save')
            messages.success(request, "✅ Product added successfully")
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
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = str(data.get("item_id"))
        action = data.get("action")

        # ---------------- LOGGED IN ----------------
        if request.user.is_authenticated:
            cart_item = get_object_or_404(
                CartItem,
                id=item_id,
                cart__user=request.user
            )

            if action == "inc":
                cart_item.quantity += 1
            elif action == "dec":
                cart_item.quantity -= 1
                if cart_item.quantity <= 0:
                    cart_item.delete()
                    return JsonResponse({"status": "success", "quantity": 0})

            cart_item.save()

            return JsonResponse({
                "status": "success",
                "quantity": cart_item.quantity,
                "subtotal": float(cart_item.total_price()),
                "cart_count": cart_item.cart.items.count(),
                "cart_total": float(cart_item.cart.get_total_price())
            })

        # ---------------- GUEST ----------------
        else:
            cart = request.session.get('cart', {})

            if item_id in cart:
                if action == "inc":
                    cart[item_id] += 1
                elif action == "dec":
                    cart[item_id] -= 1
                    if cart[item_id] <= 0:
                        del cart[item_id]
                        request.session['cart'] = cart
                        return JsonResponse({"status": "success", "quantity": 0})

            request.session['cart'] = cart
            request.session.modified = True

            product = Product.objects.get(id=item_id)
            quantity = cart.get(item_id, 0)
            subtotal = product.product_price * quantity

            cart_total = 0
            for pid, qty in cart.items():
                p = Product.objects.get(id=pid)
                cart_total += p.product_price * qty

            return JsonResponse({
                "status": "success",
                "quantity": quantity,
                "subtotal": float(subtotal),
                "cart_count": sum(cart.values()),
                "cart_total": float(cart_total)
            })

    return JsonResponse({"status": "fail"})


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
            full_name=full_name,
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
        return redirect("cart_details_list")

    return render(request, "cart_list.html", {
        "cart_items": cart_items,
        "total": total
    })

# def cart_details_list(request):
#     orders = Order.objects.filter(user=request.user).order_by('id')
#     return render(request, "product/cart_details_list.html", {"orders": orders})

@login_required
def cart_details_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    for order in orders:
        return render(request, "product/cart_details_list.html", {"orders": orders})


@login_required
def offcanvas(request):
    return render(request, 'product/offcanvas.html')


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    if not created:
        wishlist_item.delete()
        
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    products = Product.objects.all()
    return render(request, "wish/wishlist.html", {"wishlist_items": wishlist_items, "products":products})



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

def profile(request):
    return render(request, 'navbar/profile.html')