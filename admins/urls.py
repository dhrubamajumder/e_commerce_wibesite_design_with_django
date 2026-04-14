

from django.urls import path
from .views import BranchListView, BranchCreateView, BranchUpdateView, BranchDeleteView
from . import views

urlpatterns = [
    path('branches/', BranchListView.as_view(), name='branch_list'),         
    path('branches/add/', BranchCreateView.as_view(), name='branch_add'),  
    path('branches/<int:pk>/edit/', BranchUpdateView.as_view(), name='branch_edit'),  
    path('branches/<int:pk>/delete/', BranchDeleteView.as_view(), name='branch_delete'),
    
    path('fund/list/', views.fund_list, name='fund_list'),
    path('fund/form/', views.fund_create, name='fund_create'),
    path('fund/update/<int:id>/', views.fund_update, name='fund_update'),
    path('fund/delete/<int:id>/', views.fund_delete, name='fund_delete'),
    
    
    path('fund-transfer/list/', views.fund_transfer_list, name='fund_transfer_list'),
    path('fund-transfer/create/', views.fund_transfer_create, name='fund_transfer_create'),
    path('fund-transfer/delete/<int:id>/', views.fund_transfer_delete, name='fund_transfer_delete'),
    
    
    path('expense-category/list/', views.expense_category_view, name='expense_category_list'),
    path('expense-category/update/<int:id>/', views.expense_category_update, name='expense_category_update'),
    path('expense-category/delete/<int:id>/', views.expense_category_delete, name='expense_category_delete'),
    
    path('income-category/list/', views.income_category_list, name='income_category_list'),
    path('income-category/update/<int:id>/', views.income_category_update, name='income_category_update'),
    path('income-catgory/delete/<int:id>/', views.income_category_delete, name='income_category_delete'),
    
    path('customer-payment/list/', views.customer_payment_list, name='customer_payment_list'),
    path('customer-payment/create/', views.customer_payment_create, name='customer_payment_create'),
    path('customer-payment/update/<int:id>/', views.customer_payment_update, name='customer_payment_update'),
    path('customer_payment/delete/<int:id>/', views.customer_payment_delete, name='customer_payment_delete'),
    
    path('supplier-payment/list/', views.payment_list, name='supplier_payment_list'),
    path('supplier-payment/create/', views.payment_create, name='supplier_payment_create'),
    path('supplier-payment/<int:id>/update/', views.payment_update, name='payment_update'),
    path('supplier-payment/<int:id>/delete/', views.payment_delete, name='payment_delete'),

    path('expenses/list/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:id>/update/', views.expense_update, name='expense_update'),
    path('expenses/<int:id>/delete/', views.expense_delete, name='expense_delete'),

    path('income/list/', views.other_income_list, name='other_income_list'),
    path('income/create/', views.other_income_create, name='other_income_create'),
    path('income/<int:id>/update/', views.other_income_update, name='other_income_update'),
    path('income/<int:id>/delete/', views.other_income_delete, name='other_income_delete'),
    
    path('slider/', views.user_slider_list, name='user_slider_list'),
    
    path('sliders/', views.slider_list, name='slider_list'),
    path('sliders/create/', views.slider_create, name='slider_create'),
    path('sliders/update/<int:pk>/', views.slider_update, name='slider_update'),
    path('sliders/delete/<int:pk>/', views.slider_delete, name='slider_delete'),
    
    path('client-reviews/', views.client_review_list, name='client_review_list'),
    path('client-review/add/', views.client_review_create_update, name='client_review_add'),
    path('client-review/edit/<int:id>/', views.client_review_create_update, name='client_review_edit'),
    path('client-review/delete/<int:id>/', views.client_review_delete, name='client_review_delete'),
    
]
