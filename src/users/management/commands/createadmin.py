from django.core.management.base import BaseCommand, CommandError
from users.models import Users, Roles
from django.contrib.auth.hashers import make_password
import sys

class Command(BaseCommand):
    help = 'Create Admin user.'

    # def add_arguments(self, parser):
    #     parser.add_argument('total', type=int, help='Indicates the number of users to be created')

    def handle(self, *args, **kwargs):
        first_name = None
        last_name = None
        email = None
        password = None
        while not first_name:
            first_name = input('Enter first_name -> ')
        while not last_name:
            last_name = input('Enter last_name -> ')
        while not email:
            email = input('Enter email -> ')
        while not password:
            password = input('Enter password -> ')
        user = Users(first_name=first_name,last_name=last_name,email=email, password=make_password(password))        
        user.save()
        admin_role = Roles(role="admin", user = user)
        admin_role.save()
        print('<-// Administrator created. \\\->')