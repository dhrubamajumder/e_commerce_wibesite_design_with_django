
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('', views.product_list, name='product_list'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('content/', views.content, name='content'),
    
    path('cart/', views.cart_list, name='cart_list'),
    path('get-cart-items/', views.get_cart_items, name='get_cart_items'),
    
    path("cart-items-json/", views.cart_items_json, name="cart_items_json"),
    path('order-details/', views.user_order_list, name='user_order_list'),
    path('order-details/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    
    path('cart/json/', views.cart_json, name='cart_json'),
    
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
    
    path('profile-list/', views.profile_list, name='profile_list'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('demo/', views.demo, name='demo'),
    
    #----------------------------------------------------------------------------
    #------------------------------   Admin URLs   ------------------------------
    #----------------------------------------------------------------------------
    
    path('admin-panel/dashboards/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/category/list/', views.category_list, name='category_list'),
    path('admin-panel/category/create/', views.category_create, name='category_create'),
    path('admin-panel/products/', views.product, name='product'),
    path('admin-panel/products/<int:category_id>/', views.product_list, name='product_by_category'),
    path('admin-panel/product/create/', views.product_create, name='product_create'),
    path('admin-panel/stock/', views.stock_list, name='stock_list'),
    
    path('admin-panel/order-list/', views.admin_order_list, name='admin_order_list'),
    path('admin-panel/order-list/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    
    path('admin-panel/profile/list/', views.admin_profile_list, name='admin_profile_list'),
    path('admin-panel/profile/update/', views.admin_profile_update, name='admin_profile_update'),
    
    path('admin-panel/supplier/', views.supplier_list, name='supplier'),
    path('admin-panel/supplier/create/', views.supplier_create, name='supplier_create'),
    path('admin-panel/supplier/<int:id>/', views.supplier_update, name='supplier_update'),
    path('admin-panel/supplier/<int:id>/delete/', views.supplier_delete, name='supplier_delete'),
    
    path('admin-panel/settings/list/', views.settings_list, name='settings_list'),
    path('admin-panel/setting/create/', views.setting_create, name='setting_create'),
    path('admin-panel/settings/update/<int:pk>/', views.setting_update, name='settings_update'),
        
    path('admin-panel/customer/', views.customer_list, name='customer'),
    path('admin-panel/customer/create/', views.customer_create, name='customer_create'),
    path('admin-panel/customer/update/<int:pk>/', views.customer_update, name='customer_update'),
    path('admin-panel/customer/delete/<int:pk>/', views.customer_delete, name='customer_delete'),
    
    path('admin-panel/purchases/', views.purchase_list, name='purchase_list'),
    path('admin-panel/purchases/create/', views.purchase_create, name='purchase_create'),
    
    path('admin-panel/user/list/', views.user_list, name='user_list'),
    path('admin-panel/user/create/', views.add_user, name='user_create'),
    path('admin-panel/user/update/<int:id>/', views.edit_user, name='user_update'),
    path('admin-panel/user/delete/<int:id>/', views.delete_user, name='user_delete'),

    path('admin-panel/permission/list/', views.permission_list, name='permission_list'),
    path('admin-panel/permission/create/', views.permission_create, name='permission_create'),
    
    path('admin-panel/role/list/', views.role_list, name='role_list'),
    path('admin-panel/role/create/', views.role_create, name='role_create'),
    path('admin-panel/role/<int:role_id>/update/', views.role_update, name='role_update'),
    path('admin-panel/role/<int:pk>/delete/', views.role_delete, name='role_delete'),

]
