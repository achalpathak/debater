from django.urls import path,include
from . import views

urlpatterns = [
      path('auth/token/', views.get_token),
      path('auth/token/refresh/', views.get_token_refresh),
      path('auth/register/', views.register),
]