from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid6 import uuid7


class User(AbstractUser):
    """Usuario de SCHOBRAS.CL.

    Existe desde la primera migración para poder agregar campos y roles
    (editora / administrador) sin migrar el modelo de usuario más adelante.
    La PK es UUID v7 como en el resto de los modelos (ADR-0001). No hereda de
    BaseModel porque AbstractUser ya define sus propias fechas.
    """

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.get_username()
