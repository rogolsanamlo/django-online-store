"""URL configuration for the shop project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("apps.main.urls", namespace='main')),
    path('accounts/', include("apps.accounts.urls", namespace='accounts')),
    path('products/', include("apps.products.urls", namespace='products')),
    path('orders/', include("apps.orders.urls", namespace='orders')),
    path('discounts/', include("apps.discounts.urls", namespace='discounts')),
    path('payments/', include("apps.payments.urls", namespace='payments')),
    path('warehouses/', include("apps.warehouses.urls", namespace='warehouses')),
    path('csf/', include("apps.comment_scoring_favorites.urls", namespace='csf')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('search/', include("apps.search.urls", namespace='search')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.main.views.handler404'
