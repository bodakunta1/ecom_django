from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'stock', 'available')
    list_filter = ('available', 'category')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id','user','session_key','created','active')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart','product','quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','full_name','email','total','status','created')