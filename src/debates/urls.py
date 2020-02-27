from django.urls import path,include
from . import views

urlpatterns = [
    path('debates/create-debate', views.create_debate),
    path('debates/view-all', views.view_all_debates),
    path('debates/participate', views.participate),
]