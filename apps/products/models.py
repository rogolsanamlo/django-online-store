from datetime import datetime

from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.db.models import Avg, Sum
from django.urls import reverse
from django.utils import timezone

from middlewares.middlewares import get_current_request
from utils import FileUploud


class Brand(models.Model):
    brand_title = models.CharField(max_length=50, verbose_name='نام برند')
    file_upload = FileUploud('images', 'brand')
    image_name = models.ImageField(upload_to=file_upload, verbose_name='تصویر برند کالا')
    slug = models.SlugField('نامک (بخش انتهایی آدرس)', max_length=200, null=True)

    def __str__(self):
        return self.brand_title

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برند ها'


class ProductGroup(models.Model):
    group_title = models.CharField(max_length=100, verbose_name='عنوان گروه کالا')
    file_uplod = FileUploud('images', 'product_group')
    image_name = models.ImageField(upload_to=file_uplod, verbose_name='تصویر گروه کالا')
    description = RichTextUploadingField('توضیحات', config_name='special', blank=True)
    is_active = models.BooleanField(default=True, blank=True, verbose_name='فعال/غیر فعال')
    group_parent = models.ForeignKey(
        'ProductGroup',
        on_delete=models.CASCADE,
        verbose_name='والد گروه کالا',
        blank=True,
        null=True,
        related_name='groups',
    )
    slug = models.SlugField('نامک (بخش انتهایی آدرس)', max_length=200, null=True, unique=True)
    register_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ درج')
    published_date = models.DateTimeField(default=timezone.now, verbose_name='تاریخ انتشار')
    update_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ اخرین به روزرسانی')

    def __str__(self):
        return self.group_title

    class Meta:
        verbose_name = 'گروه کالا'
        verbose_name_plural = 'گروه های کالا'


class Feature(models.Model):
    feature_name = models.CharField(max_length=100, verbose_name='نام ویزگی')
    product_group = models.ManyToManyField(
        ProductGroup,
        verbose_name='گروه کالا',
        related_name='features_of_groups',
    )

    def __str__(self):
        return self.feature_name

    class Meta:
        verbose_name = 'ویزگی '
        verbose_name_plural = 'ویزگی ها'


class FeatureValue(models.Model):
    value_title = models.CharField(max_length=100, verbose_name='عنوان مقدار')
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='ویزگی',
        related_name='feature_values',
    )

    def __str__(self):
        return f'{self.id}-{self.value_title}'

    class Meta:
        verbose_name = 'مقدار ویزگی'
        verbose_name_plural = 'مقادیر ویزگی ها'


class Product(models.Model):
    product_name = models.CharField(max_length=500, verbose_name='نام کالا')
    file_upload = FileUploud('images', 'product_group')
    image_name = models.ImageField(upload_to=file_upload, verbose_name='تصویر کالا')
    product_group = models.ManyToManyField(
        ProductGroup,
        verbose_name='گروه کالا',
        related_name='products_of_groups',
    )
    price = models.PositiveIntegerField(default=0, verbose_name='قیمت کالا')
    brand = models.ForeignKey(
        'Brand',
        on_delete=models.CASCADE,
        verbose_name='برند کالا',
        null=True,
        related_name='products_of_brands',
    )
    is_active = models.BooleanField(default=True, blank=True, verbose_name='فعال/غیر فعال')
    slug = models.SlugField('نامک (بخش انتهایی آدرس)', max_length=200, null=True, unique=True)
    summery_description = models.TextField('خلاصه توضیحات', blank=True, default='', null=True)
    description = RichTextUploadingField('توضیحات', config_name='special', blank=True)
    register_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ درج')
    published_date = models.DateTimeField(default=timezone.now, verbose_name='تاریخ انتشار')
    update_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ اخرین به روزرسانی')
    features = models.ManyToManyField(
        Feature,
        through='ProductFeature',
        verbose_name='ویژگی\u200cها',
    )

    def __str__(self):
        return self.product_name

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def get_price_by_discount(self):
        list1 = []
        now = datetime.now()
        for dbd in self.discount_basket_details2.select_related('discount_basket'):
            basket = dbd.discount_basket
            if basket.is_active and basket.start_date <= now <= basket.end_date:
                list1.append(dbd.discount_basket.discount)
        discount = 0
        if len(list1) > 0:
            discount = max(list1)
        return int(self.price - self.price * discount / 100)

    def get_number_in_warehouse(self):
        sum1 = self.warehouse_products.filter(warehouse_type_id=1).aggregate(Sum('qty'))
        sum2 = self.warehouse_products.filter(warehouse_type_id=2).aggregate(Sum('qty'))
        input = 0
        if sum1['qty__sum'] != None:
            input = sum1['qty__sum']
        output = 0
        if sum2['qty__sum'] != None:
            output = sum2['qty__sum']
        return input - output

    def get_user_score(self):
        request = get_current_request()
        if request is None or not request.user.is_authenticated:
            return 0
        user_score = self.scoring_product.filter(scoring_user=request.user).first()
        return user_score.score if user_score else 0

    def get_average_score(self):
        avgScore = self.scoring_product.all().aggregate(Avg('score'))['score__avg']
        if avgScore == None:
            avgScore = 0
        return avgScore

    def get_user_favorite(self):
        request = get_current_request()
        if request is None or not request.user.is_authenticated:
            return False
        return self.favorite_product.filter(favorite_user=request.user).exists()

    def getMainProductGroups(self):
        group = self.product_group.first()
        return group.id if group else None

    class Meta:
        verbose_name = ' کالا'
        verbose_name_plural = ' کالا ها'


class ProductFeature(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='کالا',
        related_name='product_feature',
    )
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, verbose_name='ویزگی')
    value = models.CharField(max_length=100, verbose_name='مقدار ویزگی کالا')
    filter_value = models.ForeignKey(
        FeatureValue,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='ویژگی برای فیلتر',
    )

    def __str__(self):
        return f'{self.product}-{self.feature}:{self.value}'

    class Meta:
        verbose_name = 'ویزگی محصول'
        verbose_name_plural = 'ویزگی های محصولات'


class ProductGallery(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='کالا',
        related_name='gallery_images',
    )
    file_uplod = FileUploud('images', 'product_gallery')
    image_name = models.ImageField(upload_to=file_uplod, verbose_name='تصویر کالا')

    class Meta:
        verbose_name = 'تصویر'
        verbose_name_plural = 'تصاویر'
