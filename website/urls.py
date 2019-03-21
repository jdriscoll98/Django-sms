from django.conf.urls import url, include

from . import views
from .views import SMS, AuthPage, PaymentView, ThankYouPage, PlaidAuth

# Application Routes (URLs)

app_name = 'website'

urlpatterns = [
    # General Page Views
    url(r'^$', views.homepage_view, name='homepage'),
    url(r'^sms/(?P<slug>[\w-]+)/$', SMS.as_view(), name='sms'),
    url(r'^auth/(?P<slug>[\w-]+)/$', AuthPage.as_view(), name='auth_page'),
    url(r'^payment/$', PaymentView.as_view(), name='payment'),
    url(r'^thanks/$', ThankYouPage.as_view(), name='thanks'),
    url(r'^plaid_auth/(?P<slug>[\w-]+)$', PlaidAuth.as_view(), name='plaid_auth'),
]
