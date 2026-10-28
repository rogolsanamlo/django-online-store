from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    # partials rendered with {% render_partial %}
    path('cheapest_products/', views.get_cheapest_products, name="cheapest_products"),
    path('last_products/', views.get_last_products, name="last_products"),
    path('popular_product_groups/', views.get_popular_product_groups, name="popular_product_groups"),
    path('related_products/<slug:slug>/', views.get_related_products, name="related_products"),
    path('nav_groups/', views.get_nav_groups, name="nav_groups"),
    path('product_groups_partial/', views.get_product_groups_menu, name="product_groups_partial"),
    path('brands_partial/<slug:slug>/', views.get_brands, name="brands_partial"),
    path('features_for_filter/<slug:slug>/', views.get_features_for_filter, name="features_for_filter"),
    path('compare_table/', views.compare_table, name="compare_table"),

    # pages
    path('product_details/<slug:slug>/', views.ProductDetailView.as_view(), name="product_detail"),
    path('product_groups/', views.ProductGroupsView.as_view(), name="product_groups"),
    path('products_of_group/<slug:slug>/', views.ProductsByGroupView.as_view(), name="products_of_group"),
    path('compare_list/', views.ShowCompareListView.as_view(), name="compare_list"),

    # ajax
    path('status_of_compare_list/', views.status_of_compare_list, name="status_of_compare_list"),
    path('add_to_compare_list/', views.add_to_compare_list, name="add_to_compare_list"),
    path('delete_from_compare_list/', views.delete_from_compare_list, name="delete_from_compare_list"),
    path('ajax_admin/', views.get_filter_value_for_feature, name="filter_value_for_feature"),
]
