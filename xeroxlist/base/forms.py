# xerox_app/forms.py
from django import forms
from .models import Book
from django.contrib.auth.models import User

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name','price']

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=0, required=True)
    
class CustomerForm(forms.Form):
    name = forms.CharField(max_length=255, label='Your Name')
    
class SelectUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='Select User')
    


class PlaceOrderForm(forms.Form):
    username = forms.CharField(max_length=255, required=True, label='Enter Your Username')

