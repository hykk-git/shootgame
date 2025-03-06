from django.contrib import admin
from django.urls import path, include
from shootgame.views import OutFrameView
from rest_framework.documentation import include_docs_urls
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('api/', include('shootgame.urls')),
    path('', OutFrameView.as_view(), name="home"), 
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
]