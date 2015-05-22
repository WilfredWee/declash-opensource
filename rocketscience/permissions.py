from rest_framework import permissions

class IsOwnerOrReadAndPostOnly(permissions.BasePermission):
    """
    Custom permission to only allow owner to edit or delete
    a Debater object.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in ['DELETE','PUT','PATCH']:
            try:                
                return obj.owner == request.user.debateradmin
            except AttributeError:
                return obj.session.owner == request.user.debateradmin
        return True

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            return obj.owner == request.user.debateradmin
        except AttributeError:
            return obj.session.owner == request.user.debateradmin

class IsOwnerOrReadOpenedSessionsOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            try:
                return obj.session.openForReg or (request.user.debateradmin == obj.session.owner)
            except AttributeError:
                return obj.openForReg or (request.user.debateradmin == obj.owner)
        return True

class IsOwnerToDeclashify(permissions.BasePermission):
    def has_object_permission(self, request, view):
        if request.method.QUERY_PARAMS.get('declashify', None) == True:
            return obj.owner == request.user.debateradmin