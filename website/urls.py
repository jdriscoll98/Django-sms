from django.conf.urls import url, include

from . import views
from .views import SMS

# Application Routes (URLs)

app_name = 'website'

urlpatterns = [
    # General Page Views
    url(r'^$', views.homepage_view, name='homepage'),
    url(r'^sms/$', SMS.as_view(), name='sms'),

]
