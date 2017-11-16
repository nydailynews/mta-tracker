"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import app
import mta
import views 
import os
try:
        user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
except KeyError:
        user_paths = []
print(dir(mta))

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.mode_index),
    url(r'^(?P<mode>subway)/', mta.views.mode_detail.as_view(), name='mode_detail'),
    url(r'^(?P<mode>subway)/(?P<year>[0-9]{4})', mta.views.mode_year_archive.as_view(), name='mode_year_archive'),
    #url(r'^(?P<mode>subway)/(?P<year>[0-9]{4})', mta.views.mode_year_archive.as_view(), name='mode_year_archive'),
]
