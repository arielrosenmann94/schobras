from django.db import models
from uuid6 import uuid7


class BaseModel(models.Model):
    """Base abstracta de todos los modelos: PK UUID v7 y marcas de tiempo.

    El UUID v7 es ordenable por fecha de creación (ADR-0001).
    """

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    created_at = models.DateTimeField("creado", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        abstract = True
