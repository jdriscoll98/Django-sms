from django.conf.urls import url, include

from . import views

# Application Routes (URLs)

app_name = 'website'

urlpatterns = [
    	# General Page Views
		url(r'^$', views.homepage_view, name='homepage'),
]
