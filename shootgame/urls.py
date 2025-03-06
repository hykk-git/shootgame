from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/frame/', views.FrameView.as_view(), name='frame'),
    path('api/spawn/', views.SpawnView.as_view(), name='spawn'),
    path('api/fire/', views.FireView.as_view(), name='fire'),
    path('api/update/', views.UpdateView.as_view(), name='update'),
    path('api/collision/', views.CollisionView.as_view(), name='collision'),
]