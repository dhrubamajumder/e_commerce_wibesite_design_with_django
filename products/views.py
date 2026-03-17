from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . models import Category, Product, Cart, Order, CartItem, OrderItem, Wishlist
from . forms import ProductForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Product
import json

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

    if category_id:
        products = Product.objects.filter(
            category_id=category_id
        ).order_by('-id')
    else:
        products = Product.objects.all().order_by('-id')

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
        'wishlist_products': wishlist_products
    }

    return render(request, 'product/product_list.html', context)


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

@login_required
def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        action = data.get('action')

        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )

            if action == 'inc':
                cart_item.quantity += 1

            elif action == 'dec':
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                else:
                    cart_item.delete()
                    return JsonResponse({
                        "status": "success",
                        "quantity": 0,
                        "subtotal": 0,
                        "cart_count": cart_item.cart.items.count(),
                        "cart_total": float(cart_item.cart.get_total_price())
                    })

            cart_item.save()

            return JsonResponse({
                "status": "success",
                "quantity": cart_item.quantity,
                "subtotal": float(cart_item.total_price()),
                "cart_count": cart_item.cart.items.count(),
                "cart_total": float(cart_item.cart.get_total_price())
            })

        except CartItem.DoesNotExist:
            return JsonResponse({"status": "fail"})

    return JsonResponse({"status": "fail"})



@login_required
def remove_item(request, pk):
    if request.method == "POST":
        # Only delete items that belong to the user's cart
        item = CartItem.objects.filter(id=pk, cart__user=request.user).first()
        if not item:
            return JsonResponse({"status": "fail", "message": "Item does not exist"}, status=404)

        item.delete()

        cart = item.cart
        cart_total = sum(ci.total_price() for ci in cart.items.all())

        return JsonResponse({
            "status": "success",
            "cart_count": cart.items.count(),
            "cart_total": f"{cart_total:.2f}"
        })

    return JsonResponse({"status": "fail"}, status=400)



@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, id=pk)

    # Get the latest cart for the user or create one
    cart = Cart.objects.filter(user=request.user).order_by('-created_at').first()
    if not cart:
        cart = Cart.objects.create(user=request.user)

    # Add or update the cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({
        "id": cart_item.id,
        "name": product.name,
        "price": float(product.product_price),
        "image": product.image.url if product.image else "",
        "quantity": cart_item.quantity,
        "subtotal": float(cart_item.total_price()),
        "cart_count": cart.items.count(),
        "cart_total": float(cart.get_total_price()),
    })
    
    
    
@login_required
def get_cart_items(request):
    # Get the cart for this user
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return JsonResponse([], safe=False)  # empty list if no cart exists

    cart_items = CartItem.objects.filter(cart=cart)

    items = [{
        "id": item.id,
        "name": item.product.name,
        "price": float(item.product.product_price),
        "image": item.product.image.url if item.product.image else "",
        "quantity": item.quantity,
        "subtotal": float(item.total_price())
    } for item in cart_items]

    return JsonResponse(items, safe=False)


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
    # ইউজারের কার্ট আইটেমগুলো নিয়ে আসা
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

        # 1️⃣ Order তৈরি
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            delivery_date=delivery_date,
            payment_method=payment,
            total_amount=total
        )

        # 2️⃣ Cart এর প্রতিটি item কে OrderItem হিসেবে যোগ করা
        order_items = []
        for item in cart_items:
            order_items.append(OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.product_price
            ))
        OrderItem.objects.bulk_create(order_items)

        # 3️⃣ Cart খালি করা
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

def cart_details_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    for order in orders:
        return render(request, "product/cart_details_list.html", {"orders": orders})


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
    return render(request, "wish/wishlist.html", {"wishlist_items": wishlist_items})



def wish(request):
    products = Product.objects.all()
    return render(request, 'wish/wish.html', {'products':products})