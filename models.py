from django.db import models
from datetime import datetime


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100) 
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    

