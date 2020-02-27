from django.db import models
from users.models import Users
# Create your models here.

class Debates(models.Model):
    title = models.CharField(max_length = 255)
    description = models.CharField(max_length = 255)
    winner = models.ForeignKey(Users, on_delete = models.CASCADE, null = True, blank = True, related_name = "winner_user")
    status = models.BooleanField(default = True)
    for_user = models.ForeignKey(Users, on_delete = models.CASCADE, null = True, blank = True, related_name = "for_user")
    against_user = models.ForeignKey(Users, on_delete = models.CASCADE, null = True, blank = True, related_name = "against_user")
    is_created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'debates'
        
class DebatesPost(models.Model):
    debates = models.ForeignKey('Debates', on_delete = models.CASCADE)
    post = models.CharField(max_length = 255)
    side = models.CharField(max_length = 45)
    debater = models.ForeignKey(Users, on_delete = models.CASCADE)
    vote_up = models.IntegerField(default = 0)
    vote_downs = models.IntegerField(default = 0)
    is_created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'debates_post'
        
        
class SuggestedDebates(models.Model):
    title = models.CharField(max_length = 255)
    description = models.CharField(max_length = 255)
    debater = models.ForeignKey(Users, on_delete = models.CASCADE)
    is_created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'suggested_debates'