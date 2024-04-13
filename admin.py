from typing import Any
from django.contrib import admin
from  .models import Product
from django.contrib import  messages


# Register your models here.

class ProductAdmin(admin.ModelAdmin):

    list_display = ['name', 'description', 'price', 'stock', 'total_price', 'created_time', 'last_updated']
    list_per_page = 10
    search_fields = ['title', 'content']
    ordering = ['name', 'stock']
    list_filter = ['last_updated']
    readonly_fields = ['created_time', 'last_updated']

    def total_price(self,obj):
        return obj.price * obj.stock

    def save_model(self, request: Any, obj, form: Any, change:Any) ->None:
        if obj.price > 0 and obj.stock > 0:
            return super().save_model(request, obj, form, change)
        
        messages.add_message(request, messages.INFO, "price and stock value  must be greater than zero")
        messages.error(request, "Negative values can't be accepted")
   
admin.site.register(Product,ProductAdmin)
