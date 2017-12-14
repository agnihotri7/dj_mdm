"""dj_mdm URL Configuration

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
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from . import views


urlpatterns = [
    url(r'^ssl-cert/$', views.ssl_cert, name='ssl-cert'),
    url(r'^enroll/$', views.enroll, name='enroll'),
    url(r'^checkin/$', views.checkin, name='checkin'),
    url(r'^queue/$', views.queue, name='queue'),
    url(r'^server/$', views.server, name='server'),
    url(r'^devices/$', views.devices_list, name='devices-list'),
    url(r'^devices/(?P<pk>[0-9]+)/$', views.device_detail, name='device-detail'),
    url(r'^commands/$', views.commands_list, name='commands-list'),
]
