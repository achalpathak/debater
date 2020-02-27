def auth_exempt(f):
    def _noauth(*args, **kwargs):
        return f(*args, **kwargs)
    return _noauth