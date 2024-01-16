
from django.urls import path
from .views import book_list,add_book, remove_book, edit_book, mark_order_delivered, customer_book_list,view_cart,confirm_order,add_to_cart,order_confirmation,home,user_list

urlpatterns = [
    path('', home, name='home'), 
    path('book_list/', book_list, name='book_list'),
    path('add_book/', add_book, name='add_book'),
    path('remove_book/<int:book_id>/', remove_book, name='remove_book'),
    path('edit-book/<int:book_id>/', edit_book, name='edit_book'),
    path('mark_order_delivered/<str:username>/', mark_order_delivered, name='mark_order_delivered'),
    path('customer_book_list/', customer_book_list, name='customer_book_list'),
    path('view_cart/', view_cart, name='view_cart'),
    path('confirm_order/',confirm_order,name='confirm_order'),
    path('add_to_cart/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('confirm_order/', confirm_order, name='confirm_order'),
    path('order_confirmation/', order_confirmation, name='order_confirmation'),
    path('user_list/', user_list, name='user_list'),

]

