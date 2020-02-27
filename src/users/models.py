from django.db import models

# Create your models here.

# User model to store user authentication details.
class Users(models.Model):
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    email = models.EmailField(max_length = 45, unique = True)
    password = models.CharField(max_length = 255)    
    debates_won = models.IntegerField(default = 0)
    debates_lost = models.IntegerField(default = 0)
    #points should be updated for every voteup
    points = models.IntegerField(default = 0)
    total_debates_participated = models.IntegerField(default = 0)
    banned = models.BooleanField(default = False)
    
    class Meta:
        db_table = 'users'
class AccessToken(models.Model):
    #expires after 1day
    user = models.ForeignKey(Users, on_delete = models.CASCADE)
    token = models.CharField(max_length = 255, unique = True)
    expired_at = models.DateTimeField()

    class Meta:
        db_table = 'access_token'     
        
        
class RefreshToken(models.Model):
    #expires after 15days
    access_token = models.ForeignKey(AccessToken, on_delete = models.CASCADE)
    token = models.CharField(max_length = 255, unique = True)
    expired_at = models.DateTimeField()

    class Meta:
        db_table = 'refresh_token'     
        
        
class Roles(models.Model):
    user = models.ForeignKey(Users, on_delete = models.CASCADE)
    role = models.CharField(max_length = 255, default = 'debater')

    class Meta:
        db_table = 'roles'     
