from django.contrib import admin

from .models import Slider

admin.site.site_header = 'مدیریت فروشگاه'
admin.site.site_title = 'مدیریت فروشگاه'
admin.site.index_title = 'پنل مدیریت'


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('slider_title1', 'image_slide', 'link', 'is_active', 'register_date')
    list_filter = ('is_active',)
    search_fields = ('slider_title1',)
    ordering = ('update_date',)
    readonly_fields = ('image_slide',)
