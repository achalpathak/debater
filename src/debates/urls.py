from django.urls import path,include
from . import views

urlpatterns = [
    # to create a new debate
    path('debates/create-debate', views.create_debate),
    
    # to view all debates
    path('debates/view-all', views.view_all_debates),
    
    # to view all debates based on search
    path('debates/view-all/search', views.debates_search),
    
    # to participate in a debate
    path('debates/participate', views.participate),
    
    # to view details of a debate, to modify a debate - close/open a debate, choose a winner or modify the debate title/description
    path('debates/<int:id>', views.debate),
    
    # to view and create -> suggest a debate topic
    path('debates/suggest', views.suggest_debate),
    
    # to post on a debate
    path('debates/post', views.debate_post),
    
    # to view post of a debate and upvote and downvote
    path('debates/post/<int:id>', views.debate_post_info)
]