from django.contrib import admin


# Register your models here.
from .models import Book

from .models import Customer
from .models import CustomerOrder


admin.site.register(Book)

admin.site.register(Customer)
admin.site.register(CustomerOrder)
