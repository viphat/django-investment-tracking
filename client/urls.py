from django.urls import path

from . import views

app_name = 'client'

urlpatterns = [
  path('', views.index, name='index'),
  path('update', views.update, name='update'),
  path('sync', views.sync, name='sync'),
]