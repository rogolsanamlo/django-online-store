class CompareProduct:

    def __init__(self, request):
        self.session = request.session
        compare_product = self.session.get('compare_product')
        if not compare_product:
            compare_product = self.session['compare_product'] = []
        self.compare_product = compare_product
        self.count = len(self.compare_product)

    def __iter__(self):
        compare_product = self.compare_product.copy()
        for item in compare_product:
            yield item

    def add_to_compare_product(self, productId):
        try:
            productId = int(productId)
        except (TypeError, ValueError):
            return
        if productId not in self.compare_product:
            self.compare_product.append(productId)
        self.count = len(self.compare_product)
        self.session.modified = True

    def delete_from_compare_product(self, productId):
        try:
            product_id = int(productId)
        except (TypeError, ValueError):
            return
        if product_id in self.compare_product:
            self.compare_product.remove(product_id)
        self.count = len(self.compare_product)
        self.session.modified = True

    def clear_compare_product(self):
        self.session.pop('compare_product', None)
        self.session.modified = True
