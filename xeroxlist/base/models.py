# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Book(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

# class Customer(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.user.username

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True, default=None, null=True, blank=True)

    def __str__(self):
        return self.name




class CustomerOrder(models.Model):
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calculate total price before saving
        self.total_price = self.book.price * self.quantity
        super().save(*args, **kwargs)
        return f"{self.customer.name} - {self.quantity} books - Total Price: Rs.{self.total_price}"