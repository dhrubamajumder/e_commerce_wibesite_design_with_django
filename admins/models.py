
from django.db import models
from django.contrib.auth.models import User
from products.models import Supplier, Customer


class Branch(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField()

    def __str__(self):
        return self.name
    
    

class Fund(models.Model):
    FUND_TYPE_CHOICES = (
        ('Bank', 'Bank'),
        ('Other', 'Other'),)
    fund_name = models.CharField(max_length=150)
    fund_type = models.CharField(max_length=10, choices=FUND_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fund_name
    

#--------------------------- ExpenseCategory ------------------------
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#--------------------------- Income Category ------------------------
class IncomeCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
 
class Expense(models.Model):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.name} - {self.amount}"
    

class OtherIncome(models.Model):
    category = models.ForeignKey(IncomeCategory, on_delete=models.CASCADE)
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.name} - {self.amount}"
    
    
class SupplierPayment(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.amount}"
    
    
class CustomerPayment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.amount}"
    

class FundTransfer(models.Model):
    from_fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='transfer_from')
    to_fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='transfer_to')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_fund} → {self.to_fund} ({self.amount})"


class Slider(models.Model):
    title = models.CharField(max_length=150)
    image = models.ImageField(upload_to='slider_images/')
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    


class ClientReview(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200, blank=True, null=True)
    review = models.TextField()
    photo = models.ImageField(upload_to='client_reviews/', blank=True, null=True)
    rating = models.IntegerField(default=5)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    
    