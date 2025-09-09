from rest_framework import permissions

class IsAdminOrIsSelf(permissions.BasePermission):
    """
    Custom permission to only allow admins or the user themselves to access/edit.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Allow list action only for admins
        if view.action in ['list', 'create']:
            return request.user.is_staff or request.user.user_type == 'ADMIN'
        # Allow access for any other action (like create, retrieve, etc.) for authenticated users
        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is an admin or is accessing their own profile.
        'obj' here is the CustomUser instance.
        """
        # Admins can do anything
        if request.user.is_staff or request.user.user_type == 'ADMIN':
            return True
        
        # Any other user can only access their own profile
        return obj == request.user

class IsAdminOrStocker(permissions.BasePermission):
    """
    Allows full access to Admins and Stockers, but read-only access to others.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return request.user.is_authenticated and (
            request.user.user_type == 'ADMIN' or request.user.user_type == 'STOCKCLERK'
        )

class IsAdminOrSaleOwner(permissions.BasePermission):
    """
    Allows Admins to access all sales, but sellers can only access their own.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'ADMIN':
            return True
        
        return obj.created_by == request.user