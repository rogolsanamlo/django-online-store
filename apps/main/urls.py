from django.urls import path

from . import views
app_name = 'main'
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('sliders/', views.SliderView.as_view(), name='sliders'),
]
