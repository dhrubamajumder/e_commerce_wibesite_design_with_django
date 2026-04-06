

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
]
