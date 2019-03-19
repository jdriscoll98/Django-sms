from django.conf.urls import url, include

from . import views
from .views import SMS, AuthPage, PaymentView, ThankYouPage

# Application Routes (URLs)

app_name = 'website'

urlpatterns = [
    # General Page Views
    url(r'^$', views.homepage_view, name='homepage'),
    url(r'^sms/$', SMS.as_view(), name='sms'),
    url(r'^auth/$', AuthPage.as_view(), name='auth_page'),
    url(r'^payment/$', PaymentView.as_view(), name='payment'),
    url(r'^thanks/$', ThankYouPage.as_view(), name='thanks'),
]
