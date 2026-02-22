from django.db import models



# Create your models here.

#for sign up 
class Customer(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=25)
    mobile = models.CharField(max_length=10)
    address = models.CharField(max_length=50)

    

#Django needs the Pillow library to handle images
# for install pillow
# python -m pip install Pillow


class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    
    image_url = models.URLField(
        max_length=300,
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to='restaurants/',
        blank=True,
        null=True
    )

    cuisine = models.CharField(max_length=200)
    rating = models.FloatField()

# orders for admin panel UI

class Order(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id}"
    
class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField()
    image = models.ImageField(upload_to="menu_images/", null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

