from django.urls import path,include
from . import views

urlpatterns = [
      #to get a new pair of token
      path('auth/token/', views.get_token),
      
      #to get a new pair of token based on refresh token
      path('auth/token/refresh/', views.get_token_refresh),
      
      #to register a new user
      path('auth/register/', views.register),
      
      #to return all users
      path('users/view-all', views.users_view_all),
      
      #to return all users with search
      path('users/view-all/search', views.users_search),
      
      #to return a users, ban a user
      path('users/<int:id>', views.user_profile),

]