from django.db import models
from django.contrib.auth.models import User


# --------------------------- Category ------------------------
class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


# --------------------------- Product ------------------------
class Product(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


# --------------------------- Cart ------------------------
class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="carts", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} - {self.user.username}"
    
    def get_total_price(self):
        return sum(item.total_price() for item in self.items.all())


# --------------------------- Cart Item ------------------------
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.product.product_price

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    
class Order(models.Model):
    PAYMENT_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('bkash', 'bKash'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    delivery_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist", null=True,blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('user', 'product'),
            ('session_key', 'product'),
        )

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.product.name}"
        return f"Guest - {self.product.name}"


# ------------------------------------------

class Supplier(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.name

#--------------------------- Customer ------------------------
class Customer(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    note = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
# ----------------   System Settings   ----------------
class SystemSettings(models.Model):
    company_name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    mobile = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    vat = models.PositiveIntegerField()
    token_or_table = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=100)
    website = models.CharField(max_length=100)
    
    def __str__(self):
        return self.company_name
    
    