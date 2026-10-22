from django.contrib.auth.forms import AuthenticationForm


class PanelAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Usuario o contraseña incorrectos.",
    }
