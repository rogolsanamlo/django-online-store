from django.db.models import Q
from django.shortcuts import render
from django.views import View

from apps.products.models import Product


class SearchResultsView(View):
    def get(self, request, *args, **kwargs):
        query = (request.GET.get("q") or "").strip()
        products = Product.objects.none()
        if query:
            products = Product.objects.filter(
                Q(product_name__icontains=query) | Q(description__icontains=query),
                is_active=True,
            )
        return render(request, "search_app/search_results.html", {"products": products, "query": query})
