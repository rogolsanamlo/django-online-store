from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from .models import Slider


def media_admin(request):
    """Context processor: exposes MEDIA_URL to every template as ``media_url``."""
    return {"media_url": settings.MEDIA_URL}


def index(request):
    return render(request, "main_app/index.html")


def handler404(request, exception=None):
    return render(request, 'main_app/404.html', status=404)


class SliderView(View):
    def get(self, request):
        sliders = Slider.objects.filter(is_active=True)
        return render(request, "main_app/sliders.html", {'sliders': sliders})


class AboutView(TemplateView):
    template_name = 'main_app/about.html'


class ContactView(TemplateView):
    template_name = 'main_app/contact.html'


class TermsView(TemplateView):
    template_name = 'main_app/terms.html'

