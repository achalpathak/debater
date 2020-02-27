import sys
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Debates
from users.models import Roles
from users.shortcuts import has_permission
# Create your views here.
@api_view(['POST'])
def create_debate(request, current_user):
    """
    <-// view to create new debates by admin only //->
    """
    if request.method == 'POST':
        try:
            # only admin has permission to create new debates
            checker = has_permission(current_user, ['admin'])
            if not checker:
                raise PermissionError
            title = request.data.get('title')
            description = request.data.get('description')
            if not title or not description:
                raise ValueError("title and description are required fields.")
            debate_obj = Debates()
            debate_obj.title = title
            debate_obj.description = description
            debate_obj.save()
            res = {
                "message": "debate created successfully.",
            }
            status_code = status.HTTP_201_CREATED
            return Response(res, status_code)
        except KeyError as e:
            res = {
                    'error': 'Keys missing-{}'.format(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            print(e)
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
    
@api_view(['POST'])
def participate(request, current_user):
    """
    <-// view to create new debates by admin only //->
    """
    if request.method == 'POST':
        try:
            # only admin,moderator and debater has permission to participate in a debate
            checker = has_permission(current_user, ['admin','moderator','debater'])
            if not checker:
                raise PermissionError
            debate_id = request.data.get('debate_id')
            #choice can be only 'FOR' or 'AGAINST'
            choice = request.data.get('choice')
            if not debate_id or not choice:
                raise ValueError('debate_id and choice are compulary fields.')
            if choice != 'FOR' or choice != 'AGAINST':
                raise ValueError('valid values for choice are "FOR" or "AGAINST" only')
            debate_db = Debates.objects.filter(id = debate_id).first()
            if not debate_db:
                raise ValueError('debate doesnt exist.')
            if choice == 'FOR':
                if debate_db.for_user:
                    raise ValueError('FOR debater has already been selected.')
                debate_db.for_user = current_user.user
                debate_db.save()
            if choice == 'AGAINST':
                if debate_db.against_user:
                    raise ValueError('AGAINST debater has already been selected.')
                debate_db.against_user = current_user.user
                debate_db.save()
            res = {
                "message": "debate participation successfully - {}.".format(choice),
            }
            status_code = status.HTTP_200_OK
            return Response(res, status_code)
        except KeyError as e:
            res = {
                    'error': 'Keys missing-{}'.format(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            print(e)
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
    
    
@api_view(['GET'])
def view_all_debates(request, current_user):
    """
    <-// view all debates //->
    """
    if request.method == 'GET':
        try:
            all_debates_obj = []
            user_roles = list(Roles.objects.filter(user_id = current_user.user_id).values_list('role', flat = True))
            if 'admin' in user_roles:
                #for admin
                all_debates = Debates.objects.all()
                for debate in all_debates:
                    obj = {
                        'id':debate.id,
                        'title':debate.title,
                        'description':debate.description,
                        'status':debate.status
                    }
                    if debate.winner:
                        obj.winner = {
                            'user_id' : debate.winner.id,
                            'name': debate.winner.first_name + debate.winner.last_name,
                            'email': debate.winner.email
                        }
                    if debate.for_user:
                        obj.for_user = {
                            'user_id' : debate.for_user.id,
                            'name': debate.for_user.first_name + debate.for_user.last_name,
                            'email': debate.for_user.email
                        }
                    if debate.against_user:
                        obj.against_user = {
                            'user_id' : debate.against_user.id,
                            'name': debate.against_user.first_name + debate.against_user.last_name,
                            'email': debate.against_user.email
                        }
                    all_debates_obj.append(obj)
                    
            elif 'moderator' in user_roles:
                #for moderator
                all_debates = Debates.objects.filter(status = True)
                for debate in all_debates:
                    obj = {
                        'id':debate.id,
                        'title':debate.title,
                        'description':debate.description,
                    }
                    if debate.winner:
                        obj.winner = {
                            'user_id' : debate.winner.id,
                            'name': debate.winner.first_name + debate.winner.last_name,
                            'email': debate.winner.email
                        }
                    if debate.for_user:
                        obj.for_user = {
                            'user_id' : debate.for_user.id,
                            'name': debate.for_user.first_name + debate.for_user.last_name,
                            'email': debate.for_user.email
                        }
                    if debate.against_user:
                        obj.against_user = {
                            'user_id' : debate.against_user.id,
                            'name': debate.against_user.first_name + debate.against_user.last_name,
                            'email': debate.against_user.email
                        }
                    all_debates_obj.append(obj)
            elif 'debater' in user_roles:
                #for debater
                all_debates = Debates.objects.filter(status = True)
                for debate in all_debates:
                    obj = {
                        'id':debate.id,
                        'title':debate.title,
                        'description':debate.description,
                    }
                    if debate.winner:
                        obj.winner = {
                            'user_id' : debate.winner.id,
                            'name': debate.winner.first_name + debate.winner.last_name,
                            'email': debate.winner.email
                        }
                    if debate.for_user:
                        obj.for_user = {
                            'user_id' : debate.for_user.id,
                            'name': debate.for_user.first_name + debate.for_user.last_name,
                            'email': debate.for_user.email
                        }
                    if debate.against_user:
                        obj.against_user = {
                            'user_id' : debate.against_user.id,
                            'name': debate.against_user.first_name + debate.against_user.last_name,
                            'email': debate.against_user.email
                        }
                    all_debates_obj.append(obj)
            else:
                #for guest users
                all_debates = Debates.objects.filter(status = True)
                for debate in all_debates:
                    obj = {
                        'id':debate.id,
                        'title':debate.title,
                        'description':debate.description,
                    }
                    
                    all_debates_obj.append(obj)
            res = all_debates_obj
            status_code = status.HTTP_200_OK
            return Response(res, status_code)
        except KeyError as e:
            res = {
                    'error': 'Keys missing-{}'.format(e)}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            print(e)
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
