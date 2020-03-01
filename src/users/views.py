import sys
import jwt
from .models import Users, Roles
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.response import Response
from rest_framework import status
from .decorators import auth_exempt
from rest_framework.decorators import api_view
from .tokens import token_obtain_pair,token_obtain_refresh
from users.shortcuts import has_permission




# To import JWT settings from project "settings.py" file
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
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
    except ValidationError as e:
        res = {
            'error':'invalid email field'
        }
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
        if user:
            if user.banned:
                raise ValueError('you are banned from the system, please contact the administrator or a moderator')
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
    except ValidationError as e:
        res = {
            'error':'invalid email field'
        }
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

@auth_exempt
@api_view(['GET'])
def users_view_all(request):
    """
    <-// view all users //->
    """
    if request.method == 'GET':
        try:
            res = []
            all_users = Users.objects.filter(banned = False)
            for x in all_users:
                res.append({
                    'id':x.id,
                    'name': x.first_name + ' ' + x.last_name,
                    'email': x.email,
                    'debates_won' : x.debates_won,
                    'debates_lost' : x.debates_lost,
                    'points' : x.points,
                    'total_debates_participated' : x.total_debates_participated
                })
            status_code = status.HTTP_200_OK
            return Response(res, status=status_code)
        except KeyError as e:
            res = {
                    'error': 'Keys missing-{}'.format(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            res = {'error': str(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError:
            res = {'error': 'you are unauthorized to perform the following action.'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # will print the exception and line number for easy debugging
            print(e)
            trace_back = sys.exc_info()[2]
            line = trace_back.tb_lineno
            print(line)
            res = {'error': 'some error occured'}
            
            return Response(res, status=status.HTTP_400_BAD_REQUEST)


@auth_exempt
@api_view(['GET'])
def users_search(request):
    """
    <-// view all users based on search filter condition//->
    """
    if request.method == 'GET':
        try:
            res = []
            q = request.GET.get('q')
            if not q:
                raise ValueError('q parameter is compulsary.')
            lookups= Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email=q)
            all_users= Users.objects.filter(lookups,banned = False).distinct()
            for x in all_users:
                res.append({
                    'id':x.id,
                    'name': x.first_name + ' ' + x.last_name,
                    'email': x.email,
                    'debates_won' : x.debates_won,
                    'debates_lost' : x.debates_lost,
                    'points' : x.points,
                    'total_debates_participated' : x.total_debates_participated
                })
            status_code = status.HTTP_200_OK
            return Response(res, status=status_code)
        except KeyError as e:
            res = {
                    'error': 'Keys missing-{}'.format(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            res = {'error': str(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError:
            res = {'error': 'you are unauthorized to perform the following action.'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # will print the exception and line number for easy debugging
            print(e)
            trace_back = sys.exc_info()[2]
            line = trace_back.tb_lineno
            print(line)
            res = {'error': 'some error occured'}
            
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
def user_profile(request, current_user, id):
    """
    <-// view users based on id //->
    """
    if request.method == 'GET':
        try:
            user = Users.objects.filter(id = id).first()
            res = {
                'id':user.id,
                'name': user.first_name + ' ' + user.last_name,
                'email': user.email,
                'debates_won' : user.debates_won,
                'debates_lost' : user.debates_lost,
                'points' : user.points,
                'total_debates_participated' : user.total_debates_participated,
                'banned' : user.banned,
                'roles' : []
            }
            roles_obj = Roles.objects.filter(user = user)
            for x in roles_obj:
                res['roles'].append(str(x.role))
            status_code = status.HTTP_200_OK
            return Response(res, status=status_code)
        except KeyError as e:
            res = {
                    'error': 'Keys missing-{}'.format(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            res = {'error': str(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError:
            res = {'error': 'you are unauthorized to perform the following action.'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # will print the exception and line number for easy debugging
            print(e)
            trace_back = sys.exc_info()[2]
            line = trace_back.tb_lineno
            print(line)
            res = {'error': 'some error occured'}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        
    if request.method == 'PATCH':
        try:
            # only admin has permission to edit user
            checker = has_permission(current_user, ['admin', 'moderator'])
            if not checker:
                raise PermissionError
            user = Users.objects.filter(id = id).first()
            banned = request.data.get('banned')
            add_roles = request.data.get('add_roles')
            remove_roles = request.data.get('remove_roles')
            # checking user role before performing any action
            user_roles = list(Roles.objects.filter(user_id = user).values_list('role', flat = True))
            if 'admin' in user_roles:
                raise ValueError('cannot perform actions on admin account.')
            if add_roles:
                #only admin is allowed to add or remove role
                checker = has_permission(current_user, ['admin'])
                if not checker:
                    raise PermissionError
                for x in add_roles:
                    if x != 'moderator' and x != 'debater':
                        raise ValueError('wrong role supplied')
                    Roles(user = user, role = x).save()
            if remove_roles:
                #only admin is allowed to add or remove role
                checker = has_permission(current_user, ['admin'])
                if not checker:
                    raise PermissionError
                for x in remove_roles:
                    if x != 'moderator' and x != 'debater':
                        raise ValueError('wrong role supplied')
                    Roles.objects.filter(user = user, role = x).first().delete()
            if banned:
                user.banned = banned
            user.save()
            res = {
                "message": "user updated successfully.",
            }
            status_code = status.HTTP_200_OK
            return Response(res, status=status_code)
        except KeyError as e:
            res = {
                    'error': 'Keys missing-{}'.format(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            res = {'error': str(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError:
            res = {'error': 'you are unauthorized to perform the following action.'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # will print the exception and line number for easy debugging
            print(e)
            trace_back = sys.exc_info()[2]
            line = trace_back.tb_lineno
            print(line)
            res = {'error': 'some error occured'}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        try:
            # only admin has permission to delete a user
            checker = has_permission(current_user, ['admin'])
            if not checker:
                raise PermissionError
            user = Users.objects.filter(id = id).first()
            if not user:
                raise ValueError('user doesn\'t exists.')
            user.delete()
            res = {'message': 'user has been deleted.'}
            status_code = status.HTTP_200_OK
            return Response(res, status=status_code)
        except KeyError as e:
            res = {
                    'error': 'Keys missing-{}'.format(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            res = {'error': str(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError:
            res = {'error': 'you are unauthorized to perform the following action.'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # will print the exception and line number for easy debugging
            print(e)
            trace_back = sys.exc_info()[2]
            line = trace_back.tb_lineno
            print(line)
            res = {'error': 'some error occured'}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)