from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    

    path('', views.index, name='index'),

    path('signin/', views.signin, name='signin'),

    path('signup/', views.signup, name='signup'),

    path('add_restaurant/', views.add_restaurant, name='add_restaurant'),

    path('show_restaurant/', views.show_restaurant, name='show_restaurant'),

    path('delete_restaurant/<int:id>/', views.delete_restaurant, name='delete_restaurant'),

    path('dashboard/', views.admin_home, name='dashboard'),

    path('update/<int:id>/', views.update_restaurant, name='update_restaurant'),
    path('delete-menu/<int:id>/', views.delete_menu_item, name='delete_menu_item'),

    path('restaurant/<int:id>/', views.view_restaurant, name='view_restaurant'),
    path('update-menu/<int:id>/', views.update_menu_item, name='update_menu_item'),

    path('customer_home/', views.customer_home, name='customer_home'),
    

    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),

    path('restaurant/<int:id>/menu/', views.customer_menu, name='customer_menu'),


    path('cart/', views.cart_view, name='cart_view'),
    path('remove/<str:id>/', views.remove_from_cart, name='remove_from_cart'),

    path('increase/<str:id>/', views.increase_qty, name='increase_qty'),
    path('decrease/<str:id>/', views.decrease_qty, name='decrease_qty'),

    path('payment_success/', views.payment_success, name='payment_success'),


    



    path('checkout/', views.checkout_page, name='checkout_page'),
    path('payment/', views.payment_page, name='payment_page'),
    

    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),

  










   
]

