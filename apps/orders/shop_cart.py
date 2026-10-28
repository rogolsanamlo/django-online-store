from apps.products.models import Product


class ShopCart:
    """Session based shopping cart.

    Layout of ``session['shop_cart']``::

        {'24': {'qty': 3, 'price': 2000, 'final_price': 1800}, ...}

    Keys are product ids (as strings). Prices stored here are only for
    display; the real prices are always re-read from the database when an
    order is created.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('shop_cart')
        if not cart:
            cart = self.session['shop_cart'] = {}
        self.shop_cart = cart
        self.count = len(self.shop_cart)

    def save(self):
        self.session.modified = True

    def add_to_shop_cart(self, product, qty):
        product_id = str(product.id)
        if product_id not in self.shop_cart:
            self.shop_cart[product_id] = {
                'qty': 0,
                'price': product.price,
                'final_price': product.get_price_by_discount(),
            }
        self.shop_cart[product_id]['qty'] += max(int(qty), 1)
        self.count = len(self.shop_cart)
        self.save()

    def delete_from_shop_cart(self, product):
        self.shop_cart.pop(str(product.id), None)
        self.count = len(self.shop_cart)
        self.save()

    def update(self, product_id_list, qty_list):
        for product_id, qty in zip(product_id_list, qty_list):
            if product_id in self.shop_cart:
                try:
                    qty = int(qty)
                except (TypeError, ValueError):
                    continue
                if qty > 0:
                    self.shop_cart[product_id]['qty'] = qty
        self.save()

    def clear(self):
        self.session.pop('shop_cart', None)
        self.shop_cart = {}
        self.count = 0
        self.save()

    def __iter__(self):
        products = Product.objects.filter(id__in=self.shop_cart.keys())
        for product in products:
            # build a *new* dict: never put model instances into the session data
            data = self.shop_cart[str(product.id)]
            item = dict(data)
            item['product'] = product
            item['total_price'] = int(item['final_price'] * item['qty'])
            yield item

    def calc_total_price(self):
        return sum(int(item['final_price'] * item['qty']) for item in self.shop_cart.values())
