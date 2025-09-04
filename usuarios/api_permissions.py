from rest_framework import permissions

class IsAdminOrIsSelf(permissions.BasePermission):
    """
    Custom permission to only allow admins or the user themselves to access/edit.
    """

    def has_permission(self, request, view):
        # Allow list action only for admins
        if view.action == 'list':
            return request.user.is_staff or request.user.user_type == 'ADMIN'
        # Allow access for any other action (like create, retrieve, etc.) for authenticated users
        return request.user.is_authenticated

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