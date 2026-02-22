from django.contrib import admin
from .models import Customer
from .models import Restaurant
from .models import Order
from .models import MenuItem



# Register your models here.
admin.site.register(Customer)
admin.site.register(Restaurant)
admin.site.register(Order)
admin.site.register(MenuItem)
