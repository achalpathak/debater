import sys
import jwt
from .models import Users, Roles
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.response import Response
from rest_framework import status
from .decorators import auth_exempt
from rest_framework.decorators import api_view
from .tokens import token_obtain_pair,token_obtain_refresh




# To import JWT settings from project "settings.py" file
from django.conf import settings
JWT_AUTH = settings.JWT_AUTH

#to register user
@auth_exempt
@api_view(['POST'])
def register(request):
    try:
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        if not first_name or not last_name or not email or not password or not confirm_password:
            raise ValueError('first_name, last_name, email, password and confirm_password are compulsary fields.')
        if Users.objects.filter(email = email).exists():
            raise ValueError('User already has a registered email account.')
        if password != confirm_password:
            raise ValueError('password and confirm_password should match.')
        user = Users(
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = make_password(confirm_password)
            )
        user.full_clean()
        user.save()
        #update user role
        Roles(user = user).save()
        res = {
        'success': 'User has been registered successfully.'}
        return Response(res, status=status.HTTP_200_OK)
    except KeyError as e:
        res = {
                'error': 'Keys missing-{}'.format(e)}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as e:
        print(e)
        res = {'error': str(e)}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # will print the exception and line number for easy debugging
        print(e)
        trace_back = sys.exc_info()[2]
        line = trace_back.tb_lineno
        print(line)
        res = {
                'error': 'some error occured'}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    
    
@auth_exempt
@api_view(['POST'])
def get_token(request):
    try:
        email = request.data.get('email')
        password =request.data.get('password')
        user = Users.objects.filter(email = email).first()
        if user.banned:
            raise ValueError('you are banned from the system, please contact the administrator or a moderator')
        if user:
            if check_password(password, user.password):
                res = token_obtain_pair(user)
                status_code = status.HTTP_200_OK
            else:
                res = {"error":"wrong email password combination."}
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            res = {"error":"wrong email password combination."}
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(res, status=status_code)
    except KeyError as e:
        res = {'error': 'Keys missing-{}'.format(e)}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as e:
        res = {'error': str(e)}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        trace_back = sys.exc_info()[2]
        line = trace_back.tb_lineno
        print(line)
        res = {'error': 'Field(s) missing.'}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    
@auth_exempt    
@api_view(['POST'])
def get_token_refresh(request):
    try:
        refresh_token = request.data.get('refresh_token')
        res = token_obtain_refresh(refresh_token)
        return Response(res, status=status.HTTP_200_OK)
    except KeyError as e:
        res = {'error': 'Keys missing-{}'.format(e)}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except jwt.InvalidTokenError as e:
        res = {'error': 'Invalid token supplied.'}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as e:
        res = {'error': str(e)}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        trace_back = sys.exc_info()[2]
        line = trace_back.tb_lineno
        print(line)
        res = {'error': 'Field(s) missing.'}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
