
from .models import Roles


def has_permission(current_user, access_users):
    db_roles = list(Roles.objects.filter(user_id = current_user.user_id).values_list('role', flat = True))
    if bool(set(db_roles) & set(access_users)):
        return True
    else:
        return False
    