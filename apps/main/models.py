from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.html import format_html

from utils import FileUploud


class Slider(models.Model):
    slider_title1 = models.CharField(max_length=500, null=True, blank=True, verbose_name='متن اول')
    slider_title2 = models.CharField(max_length=500, null=True, blank=True, verbose_name='متن دوم')
    slider_title3 = models.CharField(max_length=500, null=True, blank=True, verbose_name='متن سوم')
    file_upload = FileUploud('images', 'slides')
    image_name = models.ImageField(upload_to=file_upload, verbose_name='تصویر اسلاید')
    slider_link = models.URLField(max_length=200, null=True, blank=True, verbose_name='لینک')
    is_active = models.BooleanField(default=True, blank=True, verbose_name='فعال غیر فعال')
    register_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ درج ')
    published_date = models.DateTimeField(default=timezone.now, verbose_name='تاریخ انتشار')
    update_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ اخرین به روز رسانی')

    def __str__(self):
        return f'{self.slider_title1}'

    class Meta:
        verbose_name = 'اسلاید'
        verbose_name_plural = 'اسلایدها'

    def image_slide(self):
        return format_html(
            '<img src="{}{}" style="width:80px;height:80px"/>',
            settings.MEDIA_URL,
            self.image_name,
        )
    image_slide.short_description = 'تصویر اسلاید'

    def link(self):
        if not self.slider_link:
            return '-'
        return format_html('<a href="{}" target="_blank">مشاهده</a>', self.slider_link)
    link.short_description = 'پیوندها'
