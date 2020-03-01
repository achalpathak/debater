import sys
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Debates, SuggestedDebates, DebatesPost
from users.models import Roles, Users
from users.decorators import auth_exempt
from users.shortcuts import has_permission
from django.db.models import Q

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
    
@api_view(['GET', 'PATCH'])
def debate(request, current_user, id):
    """
    <-// get debate info and modify a debate //->
    """
    if request.method == 'GET':
        try:
            user_roles = list(Roles.objects.filter(user_id = current_user.user_id).values_list('role', flat = True))
            if 'admin' in user_roles:
                #for admin
                debate = Debates.objects.filter(id = id).first()
            else:
                #for moderator, debater and guest users
                debate = Debates.objects.filter(id = id, status = True).first()
                
            obj = {
                'id':debate.id,
                'title':debate.title,
                'description':debate.description,
                'for_user':{},
                'against_user':{},
                'winner':{},
                'posts':[]
            }
            if 'admin' in user_roles:
                obj['status'] = debate.status
            if debate.winner:
                obj['winner'] = {
                    'user_id' : debate.winner.id,
                    'name': debate.winner.first_name + ' ' + debate.winner.last_name,
                    'email': debate.winner.email
                }
            if debate.for_user:
                obj['for_user'] = {
                    'user_id' : debate.for_user.id,
                    'name': (debate.for_user.first_name + ' ' + debate.for_user.last_name),
                    'email': debate.for_user.email
                }
            if debate.against_user:
                obj['against_user'] = {
                    'user_id' : debate.against_user.id,
                    'name': debate.against_user.first_name + ' ' + debate.against_user.last_name,
                    'email': debate.against_user.email
                }
            all_debates_post = DebatesPost.objects.filter(debates_id = debate.id)
            for x in all_debates_post:
                obj['posts'].append({
                    'post_id':x.id,
                    'post':x.post,
                    'vote_up':x.vote_up,
                    'vote_downs':x.vote_downs,
                    'side':x.side
                })
            res = obj
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
            # only admin has permission to edit debates
            checker = has_permission(current_user, ['admin'])
            if not checker:
                raise PermissionError
            debate_obj = Debates.objects.filter(id = id).first()
            if not debate_obj:
                raise ValueError('debate doesnt exists.')
            title = request.data.get('title')
            description = request.data.get('description')
            debate_status = request.data.get('debate_status')
            winner_user_id = request.data.get('winner_user_id')
            if title:
                debate_obj.title = title
            if description:
                debate_obj.description = description
            if debate_status:
                #to open or close a debate
                debate_obj.status = debate_status
            if winner_user_id:
                # check so that winner is only updated once
                if debate_obj.winner_id:
                    raise ValueError('winner already selected')
                
                debate_obj.winner_id = winner_user_id
                
                if int(winner_user_id) == debate_obj.for_user.id:
                    #updating wins on user profile
                    usr_obj = Users.objects.filter(id = winner_user_id).first()
                    usr_obj.debates_won+=1
                    #winner gets 5 points for winning
                    usr_obj.points += 5
                    usr_obj.save()
                    usr_obj = Users.objects.filter(id = debate_obj.against_user.id).first()
                    usr_obj.debates_lost+=1
                    usr_obj.save()
                elif int(winner_user_id) == debate_obj.against_user.id:
                    #updating wins on user profile
                    usr_obj = Users.objects.filter(id = winner_user_id).first()
                    usr_obj.debates_won+=1
                    #winner gets 5 points for winning
                    usr_obj.points += 5
                    usr_obj.save()
                    usr_obj = Users.objects.filter(id = debate_obj.for_user.id).first()
                    usr_obj.debates_lost+=1
                    usr_obj.save()
                else:
                    raise ValueError('user has not participated in debate.')
                #closing the debate after winner is selected
                debate_obj.status = False

            debate_obj.save()
            res = {
                "message": "debate updated successfully.",
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
    
    
@api_view(['GET', 'POST'])
def suggest_debate(request, current_user):
    """
    <-// view all suggested debate and create a suggested debate //->
    """
    if request.method == 'GET':
        try:
            #only admin can see the suggested debates
            checker = has_permission(current_user, ['admin'])
            if not checker:
                raise PermissionError
            res = []
            all_suggested_debates = SuggestedDebates.objects.all()
            for x in all_suggested_debates:
                res.append({
                    'id':x.id,
                    'title':x.title,
                    'description':x.description,
                    'debater_id':x.debater_id
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
    
    if request.method == 'POST':
        try:
            checker = has_permission(current_user, ['debater'])
            if not checker:
                raise PermissionError
            debate_obj = SuggestedDebates()
            
            title = request.data.get('title')
            description = request.data.get('description')
            
            if not title or not description:
                raise ValueError('title and description are compulsary fields.')
            
            debate_obj.title = title
            debate_obj.description = description
            debate_obj.debater = current_user.user
            debate_obj.save()
            
            res = {
                "message": "debate suggestion created successfully.",
            }
            status_code = status.HTTP_201_CREATED
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
    
@api_view(['POST'])
def participate(request, current_user):
    """
    <-// view to participate in a debate //->
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
            if choice != 'FOR' and choice != 'AGAINST':
                raise ValueError('valid values for choice are "FOR" or "AGAINST" only')
            debate_db = Debates.objects.filter(id = debate_id, status = True).first()
            if not debate_db:
                raise ValueError('debate doesn\'t exist.')
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
            #update participated count in user table
            usr_obj = Users.objects.filter(id = current_user.user.id).first()
            usr_obj.total_debates_participated+=1
            usr_obj.save()
            res = {
                "message": "debate participated successfully - {}.".format(choice),
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
    
@auth_exempt
@api_view(['GET'])
def view_all_debates(request):
    """
    <-// view all debates //->
    """
    if request.method == 'GET':
        try:
            all_debates_obj = []
            all_debates = Debates.objects.all()
            for debate in all_debates:
                obj = {
                    'id':debate.id,
                    'title':debate.title,
                    'description':debate.description,
                    'for_user':{},
                    'against_user':{},
                    'winner':{},
                    'posts':[]
                }
                if debate.winner:
                    obj['winner'] = {
                        'user_id' : debate.winner.id,
                        'name': debate.winner.first_name + ' ' + debate.winner.last_name,
                        'email': debate.winner.email
                    }
                if debate.for_user:
                    obj['for_user'] = {
                        'user_id' : debate.for_user.id,
                        'name': (debate.for_user.first_name + ' ' + debate.for_user.last_name),
                        'email': debate.for_user.email
                    }
                if debate.against_user:
                    obj['against_user'] = {
                        'user_id' : debate.against_user.id,
                        'name': debate.against_user.first_name + ' ' + debate.against_user.last_name,
                        'email': debate.against_user.email
                    }
                all_debates_post = DebatesPost.objects.filter(debates_id = debate.id)
                for x in all_debates_post:
                    obj['posts'].append({
                        'post_id':x.id,
                        'post':x.post,
                        'vote_up':x.vote_up,
                        'vote_downs':x.vote_downs,
                        'side':x.side
                    })
                all_debates_obj.append(obj)
            res = all_debates_obj
            status_code = status.HTTP_200_OK
            return Response(res, status_code)
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
def debates_search(request):
    """
    <-// view all debates //->
    """
    if request.method == 'GET':
        try:
            all_debates_obj = []
            q = request.GET.get('q')
            if not q:
                raise ValueError('q parameter is compulsary.')
            lookups= Q(title__icontains=q) | Q(description__icontains=q)
            all_debates= Debates.objects.filter(lookups).distinct()
            for debate in all_debates:
                obj = {
                    'id':debate.id,
                    'title':debate.title,
                    'description':debate.description,
                    'for_user':{},
                    'against_user':{},
                    'winner':{},
                    'posts':[]
                }
                if debate.winner:
                    obj['winner'] = {
                        'user_id' : debate.winner.id,
                        'name': debate.winner.first_name + ' ' + debate.winner.last_name,
                        'email': debate.winner.email
                    }
                if debate.for_user:
                    obj['for_user'] = {
                        'user_id' : debate.for_user.id,
                        'name': (debate.for_user.first_name + ' ' + debate.for_user.last_name),
                        'email': debate.for_user.email
                    }
                if debate.against_user:
                    obj['against_user'] = {
                        'user_id' : debate.against_user.id,
                        'name': debate.against_user.first_name + ' ' + debate.against_user.last_name,
                        'email': debate.against_user.email
                    }
                all_debates_post = DebatesPost.objects.filter(debates_id = debate.id)
                for x in all_debates_post:
                    obj['posts'].append({
                        'post_id':x.id,
                        'post':x.post,
                        'vote_up':x.vote_up,
                        'vote_downs':x.vote_downs,
                        'side':x.side
                    })
                all_debates_obj.append(obj)
            res = all_debates_obj
            status_code = status.HTTP_200_OK
            return Response(res, status_code)
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

@api_view(['POST'])
def debate_post(request, current_user):
    """
    <-// view to create post on a debate //->
    """
    if request.method == 'POST':
        try:
            checker = has_permission(current_user, ['debater'])
            if not checker:
                raise PermissionError
            debate_id = request.data.get('debate_id')
            post = request.data.get('post')
            if not debate_id or not post:
                raise ValueError("debate_id and post are required fields.")
            # first check if the debate exists or not
            obj = Debates.objects.filter(id = debate_id).first()
            if not obj:
                ValueError('debate doesnt exists.')
            # to create a new debate post
            debate_obj = DebatesPost(debates = obj)
            if debate_obj.debates.for_user == current_user.user:
                debate_obj.side = 'FOR'
            elif debate_obj.debates.against_user == current_user.user:
                debate_obj.side = 'AGAINST'
            else:
                raise ValueError('you are not participated in the debate.')
            debate_obj.debater = current_user.user
            debate_obj.post = post
            debate_obj.save()
            res = {
                "message": "debate post created successfully.",
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
        
    


@api_view(['GET', 'PATCH'])
def debate_post_info(request, current_user, id):
    """
    <-// view to create post on a debate //->
    """
    if request.method == 'GET':
        try:
            #only admin can see the suggested debates
            checker = has_permission(current_user, ['debater'])
            if not checker:
                raise PermissionError
            res = []
            all_debates_post = DebatesPost.objects.filter(id = id)
            for x in all_debates_post:
                res.append({
                    'debates_id':x.debates_id,
                    'post':x.post,
                    'vote_up':x.vote_up,
                    'vote_downs':x.vote_downs,
                    'side':x.side
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
        
    if request.method == 'PATCH':
        try:
            # <-// to vote up or vote down //->
            checker = has_permission(current_user, ['debater'])
            if not checker:
                raise PermissionError
            action = request.data.get('action')
            if not action:
                raise ValueError("action are required fields.")
            debate_obj = DebatesPost.objects.filter(id = id).first()
            if not debate_obj:
                ValueError('debate post doesnt exists.')
            obj = Debates.objects.filter(id = debate_obj.debates.id).first()
            if obj.for_user == current_user.user or obj.against_user == current_user.user:
                raise ValueError('participants cannot vote.')

            if action == 'UP':
                usr = Users.objects.filter(id = debate_obj.debater.id).first()
                usr.points += 1
                usr.save()
                debate_obj.vote_up +=1
            elif action == 'DOWN':
                debate_obj.vote_downs +=1
            else:
                raise ValueError('invalid input supplied for action parameter.')
            
            debate_obj.save()
            res = {
                "message": "debate post voted successfully.",
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