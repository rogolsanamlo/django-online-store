from admin_decorators import order_field, short_description
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core import serializers
from django.db.models import Q
from django.db.models.aggregates import Count
from django.http import HttpResponse
from django_admin_listfilter_dropdown.filters import DropdownFilter

from .models import (
    Brand,
    Feature,
    FeatureValue,
    Product,
    ProductFeature,
    ProductGallery,
    ProductGroup,
)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('brand_title', 'slug')
    list_filter = ('brand_title',)
    search_fields = ('brand_title',)
    ordering = ('brand_title',)


def de_active_product_group(modeladmin, request, queryset):
    res = queryset.update(is_active=False)
    message = f'گروه تعداد {res}کالا غیر فعال شد'
    modeladmin.message_user(request, message)


def active_product_group(modeladmin, request, queryset):
    res = queryset.update(is_active=True)
    message = f'تعداد گروه{res}کالا  فعال شد'
    modeladmin.message_user(request, message)


def export_json(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/json')
    serializers.serialize('json', queryset, stream=response)
    return response


class GroupFilter(SimpleListFilter):
    title = 'گروه محصولات'
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        sub_groups = ProductGroup.objects.filter(~Q(group_parent=None))
        groups = set([item.group_parent for item in sub_groups])
        return [(item.id, item.group_title) for item in groups]

    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(Q(group_parent=self.value()))
        return queryset


class ProductGroupInstanceInlineAdmin(admin.TabularInline):
    model = ProductGroup
    extra = 2


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = (
        'group_title',
        'is_active',
        'register_date',
        'group_parent',
        'slug',
        'update_date',
        'count_sub_group',
        'count_product_of_group',
    )
    list_filter = (GroupFilter, ('group_parent', DropdownFilter), 'group_title')
    search_fields = ('group_title',)
    ordering = ('group_parent', 'group_title')
    inlines = [ProductGroupInstanceInlineAdmin]
    actions = [de_active_product_group, active_product_group, export_json]
    list_editable = ['is_active']

    def get_queryset(self, *args, **kwargs):
        qs = super(ProductGroupAdmin, self).get_queryset(*args, **kwargs)
        qs = qs.annotate(sub_group=Count('groups'))
        qs = qs.annotate(produc_of_group=Count('products_of_groups'))
        return qs

    @short_description('تعداد زیر گروه ها')
    @order_field('sub_group')
    def count_sub_group(self, obj):
        return obj.sub_group

    @short_description('تعداد کالاهای گروه')
    @order_field('produc_of_group')
    def count_product_of_group(self, obj):
        return obj.produc_of_group
    de_active_product_group.short_description = ' غیر فعال کردن گروه های انتخاب شده'
    active_product_group.short_description = '  فعال کردن گروه های انتخاب شده'
    export_json.short_description = 'خروجی json از گروه های انتخاب شده '


class FeatureValueInline(admin.TabularInline):
    model = FeatureValue
    extra = 3


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('feature_name', 'display_groups', 'display_feature_values')
    list_filter = ('feature_name',)
    search_fields = ('feature_name',)
    ordering = ('feature_name',)
    inlines = [FeatureValueInline]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'product_group':
            queryset = ProductGroup.objects.filter(~Q(group_parent=None))
            kwargs['queryset'] = queryset
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def display_groups(self, obj):
        groups = obj.product_group.all()
        return ','.join([group.group_title for group in groups])

    def display_feature_values(self, obj):
        groups = obj.feature_values.all()
        return ', '.join([feature_value.value_title for feature_value in groups])
    display_groups.short_description = 'گروه های دارای این ویژگی'
    display_feature_values.short_description = 'مقادیر ممکن برای این ویژگی'


def de_active_product(modeladmin, request, queryset):
    res = queryset.update(is_active=False)
    message = f'تعداد {res}کالا غیر فعال شد'
    modeladmin.message_user(request, message)


def active_product(modeladmin, request, queryset):
    res = queryset.update(is_active=True)
    message = f'تعداد {res}کالا  فعال شد'
    modeladmin.message_user(request, message)


class ProductFeatureInLine(admin.TabularInline):
    model = ProductFeature
    extra = 5

    class Media:
        css = {'all': ('css/admin_style.css',)}
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            'js/admin_script.js',
        )


class ProductProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'price',
        'brand',
        'is_active',
        'slug',
        'update_date',
        'display_product_groups',
    )
    list_filter = (
        ('brand__brand_title', DropdownFilter),
        ('product_group__group_title', DropdownFilter),
    )
    search_fields = ('product_name',)
    ordering = ('update_date', 'product_name')
    actions = [de_active_product, active_product]
    inlines = [ProductFeatureInLine, ProductProductGalleryInline]
    de_active_product.short_description = ' غیر فعال کردن کالا های انتخاب شده'
    active_product.short_description = '  فعال کردن کالا های انتخاب شده'

    def display_product_groups(self, obj):
        groups = obj.product_group.all()
        return ', '.join([group.group_title for group in groups])
    display_product_groups.short_description = 'گروه های کالا'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'product_group':
            queryset = ProductGroup.objects.filter(~Q(group_parent=None))
            kwargs['queryset'] = queryset
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    fieldsets = (
        (
            'اطلاعات محصول',
            {
                'fields': (
                    'product_name',
                    'image_name',
                    ('product_group', 'brand', 'is_active'),
                    'price',
                    'summery_description',
                    'description',
                    'slug',
                ),
            },
        ),
        ('تاریخ و زمان', {'fields': ('published_date',)}),
    )
