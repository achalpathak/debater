import jwt
from .models import AccessToken
from rest_framework import status
from django.http import JsonResponse

# To import JWT settings from project "settings.py" file
from django.conf import settings
JWT_AUTH = settings.JWT_AUTH

class CheckAuthenticationMiddleware(object):
    def __init__(self, next_layer=None):
        self.get_response = next_layer
    
    def process_request(self,request):
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.__name__ == '_noauth':
            return view_func(request, *view_args, **view_kwargs)
        else:
            try:
                if request.META['HTTP_AUTHORIZATION']:
                    if request.META['HTTP_AUTHORIZATION'][0:6].lower() != "token ":
                        print('header content issue')
                        res = { 'error': 'Server could not verify authorization header.'}
                    else:
                        # Check if the token is verified
                        try:
                            jwt.decode(request.META['HTTP_AUTHORIZATION'][6:], JWT_AUTH['JWT_SECRET'],algorithm=JWT_AUTH['JWT_ALGORITHM'])
                            # Authorization and roles and permissions check starts below
                            db = AccessToken.objects.filter(token = request.META['HTTP_AUTHORIZATION'][6:]).first()
                            if db:
                                current_user = db
                                return view_func(request, current_user,*view_args, **view_kwargs)
                            else:
                                print('jtoken doesnt exists.')
                                res = { 'error': 'Server could not verify authorization header.'}
                                
                        except jwt.InvalidTokenError:
                            print('jwt token not verified')
                            res = { 'error': 'Server could not verify authorization header.'}
                else:
                    print('header is missing')
                    res = { 'error': 'Server could not verify authorization header.'}
            except KeyError:
                print('header is missing keyerror')
                res = { 'error': 'Server could not verify authorization header.'}
            return JsonResponse(res, status=status.HTTP_403_FORBIDDEN)
        return None

    
    def process_response(self, request, response):
        return response
    
    def __call__(self, request):
        response = self.process_request(request)
        if response is None:
            response = self.get_response(request)

        response = self.process_response(request, response)
            
        return response