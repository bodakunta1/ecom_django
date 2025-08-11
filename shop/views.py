from .models import Cart

def get_or_create_cart(request):
    """Return an active cart for the current user or session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, active=True)
        return cart

    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key, active=True)
    return cart

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Product, Category, CartItem, Order


# Product listing
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product_list.html', {'category': category, 'categories': categories, 'products': products})

# Product detail
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'shop/product_detail.html', {'product': product})

# Cart views
def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, 'shop/cart_detail.html', {'cart': cart})

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    quantity = int(request.POST.get('quantity', 1))
    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()
    return redirect('shop:cart_detail')

@require_POST
def update_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    qty = int(request.POST.get('quantity', 1))
    if qty <= 0:
        item.delete()
    else:
        item.quantity = qty
        item.save()
    return redirect('shop:cart_detail')

def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect('shop:cart_detail')

# Checkout (simple) — create Order from Cart
def checkout(request):
    cart = get_or_create_cart(request)
    if cart.items.count() == 0:
        return redirect('shop:product_list')
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        order = Order.objects.create(
            cart=cart,
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            email=email,
            address=address,
            city=city,
            postcode=postcode,
            total=cart.total,
        )
        cart.active = False
        cart.save()
        return redirect('shop:order_confirmation', order_id=order.id)
    return render(request, 'shop/checkout.html', {'cart': cart})

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/order_confirmation.html', {'order': order})