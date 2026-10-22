from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """Ingreso con el correo (sin distinguir mayúsculas) o, si no, con el nombre de usuario.

    El correo solo sirve si pertenece a exactamente un usuario; si no, se
    intenta como nombre de usuario.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if not username or password is None:
            return None
        matches = list(UserModel._default_manager.filter(email__iexact=username)[:2])
        if len(matches) == 1:
            user = matches[0]
        else:
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                # Igual que ModelBackend: cuesta lo mismo que un usuario existente.
                UserModel().set_password(password)
                return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
