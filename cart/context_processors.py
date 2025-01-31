from cart.cart import Cart

def cart_context(request):
    return {'cart': Cart(request), 'cart_count': len(Cart(request))}
