from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Usuario de SCHOBRAS.CL.

    Existe desde la primera migración para poder agregar campos y roles
    (editora / administrador) sin migrar el modelo de usuario más adelante.
    """
