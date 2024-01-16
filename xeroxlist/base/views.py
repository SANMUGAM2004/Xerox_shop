from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from .models import Book,CustomerOrder,Customer
from django.db.models import Sum
from django.contrib.auth.models import User
from .forms import BookForm,CustomerForm
from django.contrib import messages
from .forms import AddToCartForm
from django.http import Http404
from decimal import Decimal
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login


#===========================================================================================================================

def order_confirmation(request):
    return render(request, 'base/order_confirmation.html')

#===========================================================================================================================
from django.db import IntegrityError
import logging
from django.shortcuts import render, redirect
from .models import CustomerOrder, Book
from django.db import transaction



logger = logging.getLogger(__name__)

@login_required
@transaction.atomic
def confirm_order(request):
    logger.info("Confirm Order View Reached")

    if request.method == 'POST':
        logger.debug(f"Received POST request data: {request.POST}")

        # Extract the username from the form data
        user_name = request.POST.get('username', '')

        # If the 'username' is not found in the form data, check in the session
        if not user_name:
            user_name = request.session.get('username', '')
        print(user_name)

        cart = request.session.get('cart', {})

        try:
            with transaction.atomic():
                total_price = 0
                books_ordered = []

                # Get or create the associated customer based on the entered name
                customer, created = Customer.objects.get_or_create(name=user_name)

                for book_id, item in cart.items():
                    book = Book.objects.get(pk=book_id)
                    quantity = item['quantity']

                    # Create a customer order associated with the customer
                    order = CustomerOrder.objects.create(
                        customer=customer,
                        book=book,
                        quantity=quantity,
                        total_price=book.price * quantity
                    )

                    # Update the book count in the shop
                    book.count += quantity
                    book.save()

                    # Track books and total price for display
                    books_ordered.append({'name': book.name, 'quantity': quantity, 'total_price': book.price * quantity})
                    total_price += book.price * quantity

                # Clear the cart after the successful order
                request.session['cart'] = {}
                request.session['username'] = user_name  # Store the username in the session

                # Pass information to the template
                context = {
                    'user_name': user_name,
                    'books_ordered': books_ordered,
                    'total_price': total_price,
                }
                print
                return render(request, 'base/order_confirmation.html', context)

        except IntegrityError as integrity_error:
            logger.error(f"IntegrityError: {str(integrity_error)}")
            return render(request, 'base/order_error.html', {'error_message': 'Error processing order. Please try again later.'})

    logger.warning("Redirecting to customer_book_list")
    return redirect('customer_book_list')

#===========================================================================================================================

def view_cart(request): 
    username = request.GET.get('username', '')
    cart = request.session.get('cart', {})
    total_amount = 0

    # Filter out items with quantity 0
    cart_filtered = {book_id: item for book_id, item in cart.items() if item['quantity'] > 0}

    for book_id, item in list(cart_filtered.items()):    
        try: 
            book = get_object_or_404(Book, pk=book_id)
            item['name'] = book.name
            item['total_price'] = item['quantity'] * book.price
            total_amount += item['total_price']
        except Book.DoesNotExist: 
            del cart[book_id]

    return render(request, 'base/view_cart.html', {'cart': cart_filtered.values(), 'total_amount': total_amount})



    
# ============================================================================================================================= 

def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            # Get or initialize the cart from session
            cart = request.session.get('cart', {})
            price_as_float = float(book.price)

            # Extract the username from the form or session
            username = request.POST.get('username', '') or cart.get('username', '')

            # Update the cart with the selected book, quantity, and username
            if book.id in cart:
                cart[book.id]['quantity'] += quantity
            else:
                cart[book.id] = {'name': book.name, 'quantity': quantity, 'price': price_as_float, 'username': username}

            # Save the updated cart in session
            request.session['cart'] = cart

            # Redirect back to the customer book list
            return HttpResponseRedirect(reverse('customer_book_list'))

    return render(request, 'base/add_to_cart.html', {'book': book, 'form': form})



#=============================================================================================================================


def customer_book_list(request):
    # Check if the page is accessed through a reload
    if request.method == 'POST':
        username = request.POST.get('username')

        # Check if the user already has a customer profile
        if request.user.customer:
            # User already has a customer profile
            customer = request.user.customer
        else:
            # User does not have a customer profile, create one
            customer = Customer.objects.create(user=request.user)

        # Update or create the user's name
        customer.name = username
        customer.save()

        # Store the username in the session
        request.session['username'] = username

        # Redirect to the book list view for the customer
        return redirect('customer_book_list')

    if 'reload' in request.GET:
        # Clear the cart
        request.session['cart'] = {}
        
    next_url = request.GET.get('next')

    if next_url:
        # Extract the username from the query parameters
        username = request.GET.get('username', '')
        print(username)

    # Retrieve the cart from the session
    cart = request.session.get('cart', {})

    # Calculate the total book price
    total_price = sum(book['quantity'] * Book.objects.get(pk=book_id).price for book_id, book in cart.items())

    # Retrieve the list of available books
    books = Book.objects.all()

    return render(request, 'base/customer_book_list.html', {'books': books, 'cart': cart, 'total_price': total_price})


#=============================================================================================================================

def calculate_total_price(cart): 
    total_price = Decimal('0.00')  # Use Decimal for precision
    for book_id, item in cart.items(): 
        book         = get_object_or_404(Book, pk=book_id)
        quantity     = item.get('quantity', 0)  # Handle missing 'quantity' key
        total_price += book.price * quantity
    return total_price

#=============================================================================================================================
# main/views.py
from django.shortcuts import get_object_or_404, redirect
from .models import Customer, CustomerOrder, Book

def mark_order_delivered(request, username):
    # Assuming you have a Customer model that links to User
    customer = get_object_or_404(Customer, user__username=username)

    # Delete the corresponding CustomerOrders
    customer_orders = CustomerOrder.objects.filter(customer=customer)
    for order in customer_orders:
        # Reduce the books count for each ordered book
        book = order.book
        book.count -= order.quantity
        book.save()  
    customer_orders.delete()

    return redirect('user_list')


#=============================================================================================================================
from django.db.models import Sum

def user_list(request):
    users = CustomerOrder.objects.values('customer__user__username').distinct()
    user_orders = []

    for user in users:
        username = user['customer__user__username']
        orders = CustomerOrder.objects.filter(customer__user__username=username)
        total_amount = orders.aggregate(Sum('total_price'))['total_price__sum']
        books_ordered = [{'name': order.book.name, 'quantity': order.quantity} for order in orders]
        user_orders.append({'username': username, 'total_amount': total_amount, 'books_ordered': books_ordered})

    context = {'user_orders': user_orders}
    return render(request, 'base/user_list.html', context)

#=============================================================================================================================
def remove_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book_name = book.name                       # Save the book name before deleting for the warning message
    book.delete()
    
    messages.success(request, f'Book "{book_name}" has been removed.')
    return redirect('book_list')
#=============================================================================================================================
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Book "{book.name}" has been updated.')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'base/edit_book.html', {'form': form, 'book': book})
#=============================================================================================================================

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')        # Redirect to the books list page
    else:
        form = BookForm()

    return render(request, 'base/add_book.html', {'form': form})
#=============================================================================================================================
def book_list(request):
    books = Book.objects.all()
    return render(request, 'base/book_list.html', {'books': books})
#=============================================================================================================================


# @login_required
# def home(request):
#     username = request.POST.get('username')
#     user = request.user

#     try:
#         # Try to get an existing customer for the user
#         customer = Customer.objects.get(user=user)
#     except Customer.DoesNotExist:
#         # If no existing customer, create a new one
#         customer = Customer.objects.create(user=user)

#     if username:
#         # Update the username for the customer
#         user.username = username
#         user.save()
#         return redirect('customer_book_list')
    
#     return render(request, 'base/home.html', {'customer': customer})
@login_required
def home(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        # Check if the user already exists
        user, created = User.objects.get_or_create(username=username)

        # Create or get the associated customer
        customer, customer_created = Customer.objects.get_or_create(user=user, defaults={'name': username})

        if not created and not customer_created:
            # If the user and customer already exist, update the name if it's different
            if customer.name != username:
                customer.name = username
                customer.save()
                
        login(request, user)

        return redirect('customer_book_list')

    return render(request, 'base/home.html')


