"""stripe_example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^charge_card/$', 'main.views.charge_card', name="charge_card"),
    url(r'^read_csv/$', 'main.views.read_csv', name="read_csv"),
    url(r'^item_list_view/$', 'main.views.item_list_view', name="item_list_view"),
    url(r'^json_item_list/$', 'main.views.json_item_list', name="json_item_list"),
    url(r'^ups_shipping/$', 'main.views.ups_shipping', name="ups_shipping"),
    url(r'^fedex_shipping/$', 'main.views.fedex_shipping', name="fedex_shipping"),
]

