from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class PanelAccessMixin(LoginRequiredMixin):
    """Cualquier usuario con sesión iniciada entra al panel."""


class AdminRequiredMixin(PanelAccessMixin):
    """Solo el rol Administrador (o superusuario); el resto recibe 403."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_admin_role:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
