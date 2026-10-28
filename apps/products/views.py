from django.core.paginator import Paginator
from django.db.models import Q, Count, Max, Min
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .compare import CompareProduct
from .filters import ProductFilter
from .models import Brand, FeatureValue, Product, ProductGroup

PER_PAGE_CHOICES = (10, 20, 40)
DEFAULT_PER_PAGE = PER_PAGE_CHOICES[0]


def get_root_group():
    return ProductGroup.objects.filter(Q(is_active=True) & Q(group_parent=None))


def _group_with_descendants_ids(group_id):
    """Id of a group plus the ids of all its sub groups (any depth)."""
    ids = {group_id}
    frontier = [group_id]
    while frontier:
        children = list(
            ProductGroup.objects.filter(group_parent_id__in=frontier).values_list('id', flat=True)
        )
        frontier = [child for child in children if child not in ids]
        ids.update(frontier)
    return ids


def _render_product_block(request, template_name, ordering, card_type, grid_url_name):
    """Shared by the "cheapest" / "newest" blocks of the home page.

    Without ``?grid=1`` the whole block is rendered. The group tabs of the block call the same
    URL with ``?grid=1&group=<id>`` and only the product cards are returned (``group`` empty = all).
    """
    products = Product.objects.filter(is_active=True)
    group = request.GET.get('group', '')
    if group.isdigit():
        products = products.filter(product_group__in=_group_with_descendants_ids(int(group))).distinct()
    products = products.order_by(*ordering)[:3]
    context = {
        'products': products,
        'product_groups': get_root_group(),
        'card_type': card_type,
        'grid_url': reverse(grid_url_name),
    }
    if request.GET.get('grid') == '1':
        return render(request, 'product_app/partials/products_grid.html', context)
    return render(request, template_name, context)


def get_cheapest_products(request, *args, **kwargs):
    return _render_product_block(
        request, 'product_app/partials/cheapest_products.html', ('price', 'id'), 1,
        'products:cheapest_products',
    )


def get_last_products(request, *args, **kwargs):
    return _render_product_block(
        request, 'product_app/partials/last_products.html', ('-published_date', '-id'), 2,
        'products:last_products',
    )


def get_popular_product_groups(request, *args, **kwargs):
    product_groups = (
        ProductGroup.objects.filter(is_active=True)
        .annotate(count=Count('products_of_groups'))
        .order_by('-count')[:6]
    )
    context = {'product_groups': product_groups}
    return render(request, 'product_app/partials/popular_product_groups.html', context)


class ProductDetailView(View):

    def get(self, request, slug):
        product = Product.objects.filter(slug=slug, is_active=True).order_by('id').first()
        if product is None:
            raise Http404
        return render(request, 'product_app/product_detail.html', {'product': product})


def get_related_products(request, *args, **kwargs):
    current_product = get_object_or_404(Product, slug=kwargs['slug'])
    related_products = (
        Product.objects.filter(is_active=True, product_group__in=current_product.product_group.all())
        .exclude(id=current_product.id)
        .distinct()
    )
    return render(
        request,
        'product_app/partials/related_products.html',
        {'related_products': related_products},
    )


class ProductGroupsView(View):
    def get(self, request):
        product_groups = list(ProductGroup.objects.filter(is_active=True))
        for group in product_groups:  # a group counts the products of its sub groups too
            ids = _group_with_descendants_ids(group.id)
            group.total_products = (
                Product.objects.filter(product_group__in=ids).distinct().count()
            )
        product_groups.sort(key=lambda g: g.total_products, reverse=True)
        return render(
            request,
            'product_app/product_groups.html',
            {'product_groups': product_groups},
        )


def get_features_for_filter(request, *args, **kwargs):
    product_group = get_object_or_404(ProductGroup, slug=kwargs['slug'])
    feature_list = product_group.features_of_groups.all()
    feature_dict = dict()
    for feature in feature_list:
        feature_dict[feature] = feature.feature_values.all()
    return render(
        request,
        'product_app/partials/features_filter.html',
        {'feature_dict': feature_dict},
    )


def get_brands(request, *args, **kwargs):
    product_group = get_object_or_404(ProductGroup, slug=kwargs['slug'])
    group_ids = _group_with_descendants_ids(product_group.id)
    brand_list_id = (
        Product.objects.filter(is_active=True, product_group__in=group_ids).values('brand_id')
    )
    brands = (
        Brand.objects.filter(pk__in=brand_list_id)
        .annotate(count=Count('products_of_brands'))
        .filter(count__gt=0)
        .order_by('-count')
    )
    return render(request, 'product_app/partials/brands.html', {'brands': brands})


class ProductsByGroupView(View):
    def get(self, request, *args, **kwargs):
        current_group = get_object_or_404(ProductGroup, slug=kwargs['slug'])
        group_ids = _group_with_descendants_ids(current_group.id)
        products = Product.objects.filter(Q(is_active=True) & Q(product_group__in=group_ids)).distinct()
        res_aggre = products.aggregate(min=Min('price'), max=Max('price'))
        filter = ProductFilter(request.GET, queryset=products)
        products = filter.qs
        brands_filter = [v for v in request.GET.getlist('brand') if v.isdigit()]
        if brands_filter:
            products = products.filter(brand__id__in=brands_filter)
        features_filter = [v for v in request.GET.getlist('feature') if v.isdigit()]
        if features_filter:
            products = products.filter(product_feature__filter_value__id__in=features_filter).distinct()
        sort_type = request.GET.get('sort_type')
        if not sort_type:
            sort_type = '0'
        if sort_type == '1':
            products = products.order_by('price')
        elif sort_type == '2':
            products = products.order_by('-price')
        else:
            products = products.order_by('-published_date')
        group_slug = kwargs['slug']
        requested = request.GET.get('per_page', '')
        product_per_page = int(requested) if requested in {str(n) for n in PER_PAGE_CHOICES} else DEFAULT_PER_PAGE
        paginator = Paginator(products, product_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        product_count = paginator.count
        query = request.GET.copy()
        query.pop('page', None)
        show_count_product = []
        i = product_per_page
        while i < product_count:
            show_count_product.append(i)
            i *= 2
        show_count_product.append(i)
        context = {
            'products': products,
            'current_group': current_group,
            'res_aggre': res_aggre,
            'group_slug': group_slug,
            'page_obj': page_obj,
            'product_count': product_count,
            'show_count_product': show_count_product,
            'filter': filter,
            'sort_type': sort_type,
            'per_page': product_per_page,
            'per_page_choices': PER_PAGE_CHOICES,
            'query_string': query.urlencode(),
        }
        return render(request, 'product_app/products.html', context)


def get_product_groups_menu(request):
    product_groups_menu = ProductGroup.objects.filter(Q(is_active=True) & Q(group_parent=None))
    dict = {}
    for group in product_groups_menu:
        sub_group = ProductGroup.objects.filter(Q(is_active=True) & Q(group_parent=group.id))
        dict[group] = sub_group
    return render(
        request,
        'product_app/partials/product_groups_menu.html',
        {'product_groups_menu': product_groups_menu, 'dict': dict},
    )


def group_url(group):
    if not group.slug:
        return '#'
    return reverse('products:products_of_group', kwargs={'slug': group.slug})


def get_nav_groups(request):
    """Category tree (up to three levels) for the navigation menu, built from the database."""
    groups = list(ProductGroup.objects.filter(is_active=True).order_by('group_title'))
    nodes = {
        group.id: {'title': group.group_title, 'url': group_url(group), 'children': []}
        for group in groups
    }
    roots = []
    for group in groups:
        if group.group_parent_id is None:
            roots.append(nodes[group.id])
        elif group.group_parent_id in nodes:
            nodes[group.group_parent_id]['children'].append(nodes[group.id])
    return render(request, 'product_app/partials/nav_groups.html', {'groups': roots})


class ShowCompareListView(View):

    def get(self, request, *args, **kwargs):
        compare_list = CompareProduct(request)
        context = {'compare_list': compare_list}
        return render(request, 'product_app/compare_list.html', context)


def compare_table(request):
    compare_list = CompareProduct(request)
    products = list(
        Product.objects.filter(id__in=compare_list.compare_product)
        .select_related('brand')
        .prefetch_related('product_feature__feature', 'product_feature__filter_value')
    )
    features = []
    for product in products:
        for item in product.product_feature.all():
            if item.feature not in features:
                features.append(item.feature)

    rows = []
    for feature in features:
        values = []
        for product in products:
            texts = [
                item.filter_value.value_title if item.filter_value_id else item.value
                for item in product.product_feature.all()
                if item.feature_id == feature.id
            ]
            values.append(', '.join(texts) or '-')
        rows.append({'feature': feature, 'values': values})
    return render(request, 'product_app/partials/compare_table.html', {'products': products, 'rows': rows})


def status_of_compare_list(request):
    compareList = CompareProduct(request)
    return HttpResponse(compareList.count)


def add_to_compare_list(request):
    productId = request.GET.get('productId')
    if not (productId and productId.isdigit() and Product.objects.filter(id=productId).exists()):
        return HttpResponse('کالا یافت نشد', status=404)
    compareList = CompareProduct(request)
    compareList.add_to_compare_product(productId)
    return HttpResponse('کالا به لیست مقایسه اضافه شد')


def delete_from_compare_list(request):
    productId = request.GET.get('productId')
    compareList = CompareProduct(request)
    compareList.delete_from_compare_product(productId)
    return redirect('products:compare_table')


def get_filter_value_for_feature(request):
    if request.method == 'GET':
        feature_id = request.GET['feature_id']
        feature_values = FeatureValue.objects.filter(feature_id=feature_id)
        res = {fv.value_title: fv.id for fv in feature_values}
        return JsonResponse(data=res, safe=False)
