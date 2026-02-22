from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Restaurant, Order, MenuItem

from django.db.models import Sum
from django.utils import timezone


import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


# Create your views here.


#index page
def index(request):
    return render(request, 'index.html')

#sign in page


def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 🔹 Check if admin
        if username == "admin":
            request.session['admin'] = username
            return render(request, 'admin_home.html')

        # 🔹 Check normal customer
        from .models import Customer
        user = Customer.objects.filter(username=username, password=password).first()

        if user:
            request.session['username'] = username
            return redirect('customer_home')
        else:
            return render(request, 'signin.html', {'error': 'Invalid credentials'})

    return render(request, 'signin.html')


#sign up page
def signup(request):
    error = None
    # it saves the customer details on admin panel for CRUD operation
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        mobile = request.POST['mobile']
        address = request.POST['address']

         # same username + password check
        if Customer.objects.filter(username=username, password=password).exists():
            error = "Account already exists with same username and password"
        else:
            Customer.objects.create(
                username=username,
                email=email,
                password=password,
                mobile=mobile,
                address=address
            )
            return redirect('signin')

    return render(request, 'signup.html', {'error': error})





# ✅ DELETE RESTAURANT (STAYS ON SAME PAGE)
def delete_restaurant(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    restaurant.delete()
    return redirect('show_restaurant')   # ✅ redirect by URL NAME






def show_restaurant(request):
    restaurants = Restaurant.objects.all()
    return render(request, "show_restaurant.html", {"restaurants": restaurants})






def admin_home(request):

    #  Total Users
    total_users = Customer.objects.count()

    #  Active Users
    active_users = Customer.objects.count()


    # Total Restaurants
    total_restaurants = Restaurant.objects.count()

    #  Total Orders
    total_orders = Order.objects.count()

    #  Total Revenue
    total_revenue = Order.objects.aggregate(
        total=Sum('total_price')
    )['total'] or 0

    #  Today's Revenue
    today = timezone.now().date()
    todays_revenue = Order.objects.filter(
        created_at__date=today
    ).aggregate(
        total=Sum('total_price')
    )['total'] or 0

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_restaurants': total_restaurants,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'todays_revenue': todays_revenue,
    }

    return render(request, 'admin_home.html', context)






def add_restaurant(request):

    if request.method == "POST":
        print("POST HIT")

        name = request.POST.get("name")
        print("Name:", name)

        cuisine = request.POST.get("cuisine")
        rating = request.POST.get("rating")
        image_url = request.POST.get("image_url")
        image = request.FILES.get("image")

        # Convert rating safely
        rating_value = float(rating) if rating else 0

        Restaurant.objects.create(
            name=name,
            cuisine=cuisine,
            rating=rating_value,
            image=image if image else None,
            image_url=image_url if image_url else None
        )

        print("SAVED")

        restaurant = Restaurant.objects.all()
        return redirect('show_restaurant')
  
        # 👆 Use namespace if you have app_name = "delivery"

    return render(request, "add_restaurant.html")


def update_restaurant(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)

    if request.method == "POST":
        restaurant.name = request.POST.get("name")
        restaurant.cuisine = request.POST.get("cuisine")
        restaurant.rating = request.POST.get("rating")

        # Image upload from device
        if request.FILES.get("image"):
            restaurant.image = request.FILES.get("image")

        # Image URL update
        image_url = request.POST.get("image_url")
        if image_url:
            restaurant.image_url = image_url

        restaurant.save()
        return redirect("show_restaurant")

    return render(request, "update_restaurant.html", {
        "restaurant": restaurant
    })


def view_restaurant(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    menu_items = MenuItem.objects.filter(restaurant=restaurant)

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        image = request.FILES.get("image")
        image_url = request.POST.get("image_url")

        MenuItem.objects.create(
            restaurant=restaurant,
            name=name,
            description=description,
            price=price,
            image=image,
            image_url=image_url,
        )

        return redirect('view_restaurant', id=id)

    return render(request, "view.html", {
        "restaurant": restaurant,
        "menu_items": menu_items
    })

def delete_menu_item(request, id):
    item = get_object_or_404(MenuItem, id=id)
    restaurant_id = item.restaurant.id
    item.delete()
    return redirect('view_restaurant', id=restaurant_id)


def update_menu_item(request, id):
    item = get_object_or_404(MenuItem, id=id)

    if request.method == "POST":
        item.name = request.POST.get("name")
        item.description = request.POST.get("description")
        item.price = request.POST.get("price")

        image = request.FILES.get("image")
        image_url = request.POST.get("image_url")

        if image:
            item.image = image

        if image_url:
            item.image_url = image_url

        item.save()

        return redirect('view_restaurant', id=item.restaurant.id)

    return render(request, "update_menu_item.html", {"item": item})


def customer_home(request):
    from .models import Restaurant
    restaurants = Restaurant.objects.all()
    

    return render(request, 'customer_home.html', {
        'restaurants': restaurants
    })

def customer_menu(request, id):
    from .models import Restaurant, MenuItem

    restaurant = Restaurant.objects.get(id=id)
    menu_items = MenuItem.objects.filter(restaurant=restaurant)

    return render(request, 'view_item.html', {
        'restaurant': restaurant,
        'menu_items': menu_items
    })





def view_items(request, id):
    from .models import Restaurant, MenuItem

    restaurant = Restaurant.objects.get(id=id)
    items = MenuItem.objects.filter(restaurant=restaurant)

    return render(request, 'view_items.html', {
        'restaurant': restaurant,
        'items': items
    })



def add_to_cart(request, id):
    item = get_object_or_404(MenuItem, id=id)

    username = request.session.get('username')
    if not username:
        return redirect('signin')

    cart_key = f"cart_{username}"
    cart = request.session.get(cart_key, {})

    if str(id) in cart:
        cart[str(id)]['quantity'] += 1
    else:
        cart[str(id)] = {
            'name': item.name,
            'price': float(item.price),
            'quantity': 1,
            'restaurant_id': item.restaurant.id   # ✅ ADD THIS LINE
        }

    request.session[cart_key] = cart
    request.session.modified = True

    return redirect(request.META.get('HTTP_REFERER'))


def cart_view(request):
    username = request.session.get('username')
    if not username:
        return redirect('signin')

    cart_key = f"cart_{username}"
    cart = request.session.get(cart_key, {})

    total_price = 0
    for item in cart.values():
        item['subtotal'] = item['price'] * item['quantity']
        total_price += item['subtotal']

    return render(request, 'cart.html', {
        'cart': cart,
        'total_price': total_price
    })

def remove_from_cart(request, id):
    username = request.session.get('username')
    cart_key = f"cart_{username}"

    cart = request.session.get(cart_key, {})

    if str(id) in cart:
        del cart[str(id)]

    request.session[cart_key] = cart
    request.session.modified = True

    return redirect('cart_view')


def increase_qty(request, id):
    username = request.session.get('username')
    cart_key = f"cart_{username}"

    cart = request.session.get(cart_key, {})

    if str(id) in cart:
        cart[str(id)]['quantity'] += 1

    request.session[cart_key] = cart
    request.session.modified = True

    return redirect('cart_view')


def decrease_qty(request, id):
    username = request.session.get('username')
    cart_key = f"cart_{username}"

    cart = request.session.get(cart_key, {})

    if str(id) in cart:
        cart[str(id)]['quantity'] -= 1
        if cart[str(id)]['quantity'] <= 0:
            del cart[str(id)]

    request.session[cart_key] = cart
    request.session.modified = True

    return redirect('cart_view')


def checkout_page(request):
    username = request.session.get('username')
    if not username:
        return redirect('signin')

    cart_key = f"cart_{username}"
    cart = request.session.get(cart_key, {})

    if not cart:
        return redirect('cart_view')

    total_price = 0
    for item in cart.values():
        item['subtotal'] = item['price'] * item['quantity']
        total_price += item['subtotal']

    return render(request, "checkout.html", {
        "cart": cart,
        "total_price": total_price
    })



def payment_page(request):
    username = request.session.get('username')
    if not username:
        return redirect('signin')

    cart_key = f"cart_{username}"
    cart = request.session.get(cart_key, {})

    if not cart:
        return redirect('cart_view')

    total_price = 0
    for item in cart.values():
        total_price += item['price'] * item['quantity']

    amount = int(total_price * 100)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    return render(request, "payment.html", {
        "payment": payment,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "total_price": total_price
    })


def confirm_payment(request):

    payment_id = request.GET.get('payment_id')

    username = request.session.get('username')
    if not username:
        return redirect('signin')

    cart_key = f"cart_{username}"
    cart = request.session.get(cart_key, {})

    if not cart:
        return redirect('customer_home')

    total_price = 0
    for item in cart.values():
        total_price += item['price'] * item['quantity']

    customer_obj = Customer.objects.get(username=username)

    # Get restaurant from first item
    first_menu_id = list(cart.keys())[0]
    menu_item = MenuItem.objects.get(id=first_menu_id)
    restaurant_obj = menu_item.restaurant

    # Create order
    order = Order.objects.create(
        customer=customer_obj,
        restaurant=restaurant_obj,
        total_price=total_price
    )

    # Clear cart
    request.session[cart_key] = {}
    request.session.modified = True

    return render(request, "payment_success.html", {
        "order": order,
        "customer": customer_obj
    })

from .models import Order, Customer

def payment_success(request):
    username = request.session.get("username")

    if not username:
        return redirect("signin")

    customer = Customer.objects.get(username=username)

    # Get latest order (you can adjust logic later)
    order = Order.objects.filter(customer=customer).last()

    return render(request, "payment_success.html", {
        "customer": customer,
        "order": order
    })

import razorpay
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        params_dict = {
            'razorpay_order_id': data['order_id'],
            'razorpay_payment_id': data['payment_id'],
            'razorpay_signature': data['signature']
        }

        try:
            client.utility.verify_payment_signature(params_dict)

            # ✅ Mark order as paid in DB here

            return JsonResponse({"status": "success"})
        except:
            return JsonResponse({"status": "failed"})


