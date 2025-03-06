from django.urls import path
from .views import *
from django.views.generic import TemplateView

urlpatterns = [
    path('home/', OutFrameView.as_view(), name="out_frame"), 
    path('frame/', TemplateView.as_view(template_name="frame.html"), name = "frame"), 
    path('api/frame/', FrameView.as_view(), name='frame'),
    path('api/spawn/', SpawnView.as_view(), name='spawn'),
    path('api/fire/', FireView.as_view(), name='fire'),
    path('api/update/', GameUpdateView.as_view(), name='update'),
    path('api/player/status/', PlayerStatusView.as_view(), name='player_status'),
]
