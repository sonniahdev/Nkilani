from django.contrib.auth.models import User
from django.db import models

from main.models import Customers
from adminview.models import Product


class Cart(models.Model):
    customer = models.OneToOneField(Customers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.customer.name}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart for {self.cart.customer.first_name}"

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.product.price
        super(CartItem, self).save(*args, **kwargs)


class FavoriteProduct(models.Model):
    user = models.ForeignKey(Customers, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name


class Order(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, null=True)
    customer_name = models.CharField(max_length=100, null=True)
    products = models.ManyToManyField(Product, through='OrderItem')
    timestamp = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=100)
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        if self.customer:
            return f"Order #{self.id} by {self.customer.name}"
        else:
            return f"Order #{self.id} by {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    paystack_response = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.name} for {self.product.name}"


class PaymentResponse(models.Model):
    merchant_request_id = models.CharField(max_length=100)
    checkout_request_id = models.CharField(max_length=100)
    response_code = models.CharField(max_length=10)
    response_description = models.CharField(max_length=255)
    customer_message = models.CharField(max_length=255)

    def __str__(self):
        return f"Payment Response - Merchant Request ID: {self.merchant_request_id}"


class TransactionResult(models.Model):
    payment_response = models.ForeignKey(PaymentResponse, on_delete=models.CASCADE)
    result_code = models.CharField(max_length=10)
    result_description = models.CharField(max_length=255)

    def __str__(self):
        return f"Transaction Result - Payment Response: {self.payment_response.merchant_request_id}"


class TransactionDetails(models.Model):
    transaction_result = models.OneToOneField(TransactionResult, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_receipt_number = models.CharField(max_length=100)
    transaction_date = models.DateTimeField()
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"Transaction Details - Result: {self.transaction_result.result_code}"
