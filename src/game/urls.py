from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('api/play/', views.play_view, name='api_play'),
    path('api/reset/', views.reset_view, name='api_reset'),
]
