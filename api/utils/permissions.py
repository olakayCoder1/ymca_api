from rest_framework.permissions import BasePermission


class IsAppAdmin(BasePermission):
    """Allow access to authenticated users marked as admin/staff/superuser.

    This project uses a custom `is_admin` flag on the User model in addition to
    Django's `is_staff` and `is_superuser`. This permission grants access if any
    of those flags are true and the user is authenticated.
    """

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return bool(getattr(user, 'is_admin', False) or getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False))