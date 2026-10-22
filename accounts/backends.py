from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


def resolve_user(username):
    """Usuario al que corresponde lo escrito en "Correo", o None.

    El correo (sin distinguir mayúsculas) solo sirve si pertenece a exactamente
    un usuario; si no, se busca como nombre de usuario.
    """
    if not username:
        return None
    matches = list(UserModel._default_manager.filter(email__iexact=username)[:2])
    if len(matches) == 1:
        return matches[0]
    try:
        return UserModel._default_manager.get_by_natural_key(username)
    except UserModel.DoesNotExist:
        return None


class EmailOrUsernameBackend(ModelBackend):
    """Ingreso con el correo (sin distinguir mayúsculas) o, si no, con el nombre de usuario."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if not username or password is None:
            return None
        user = resolve_user(username)
        if user is None:
            # Igual que ModelBackend: cuesta lo mismo que un usuario existente.
            UserModel().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None


def lockout_username(request, credentials):
    """Clave con la que django-axes cuenta los intentos (AXES_USERNAME_CALLABLE).

    Correo en cualquier combinación de mayúsculas o nombre de usuario de la
    misma cuenta dan la misma clave (el nombre de usuario); una cuenta que no
    existe se cuenta en minúsculas. Así cada variante no suma 5 intentos nuevos.
    """
    if credentials:
        username = credentials.get("username")
    else:
        username = getattr(request, "POST", {}).get("username")
    if not username:
        return username
    user = resolve_user(username)
    return user.get_username() if user else username.lower()
