
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboards/', views.admin_dashboard, name='admin_dashboard'),
    
    path('category/list/', views.category_list, name='category_list'),
    path('category/create/', views.category_create, name='category_create'),
    
    path('products/', views.product, name='product'),
    path('', views.product_list, name='product_list'),
    path('products/<int:category_id>/', views.product_list, name='product_by_category'),
    
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('content/', views.content, name='content'),
    
    path('cart/', views.cart_list, name='cart_list'),
    path('get-cart-items/', views.get_cart_items, name='get_cart_items'),
    
    path("cart-items-json/", views.cart_items_json, name="cart_items_json"),
    path('cart-details/', views.cart_details_list, name='cart_details_list'),
    
    path('add-to-cart/<int:pk>/', views.add_to_cart, name="add_to_cart"),
    path('update-cart/', views.update_cart, name="update_cart"),
    path('remove-item/<int:pk>/', views.remove_item, name="remove_item"),
    
    path('canvas/', views.offcanvas, name='offcanvas'),
    
    path("wishlist/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    
    path('wish/', views.wish, name='wish/'),
    
    path('ajax-search/', views.ajax_search, name='ajax_search'),
    
    path('about/', views.about, name="about"),
    path('contact/', views.contact , name='contact'),
    path('faq/', views.faq , name='faq'),
    
    path('profile/', views.profile, name='profile'),
]
