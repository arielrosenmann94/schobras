from django.core.exceptions import ValidationError
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


class SiteSettings(BaseModel):
    """Datos de contacto del sitio. Registro único: usar SiteSettings.load()."""

    whatsapp = models.CharField("WhatsApp", max_length=20, blank=True)
    phone = models.CharField("teléfono", max_length=20, blank=True)
    email = models.EmailField("correo", blank=True)
    whatsapp_message = models.CharField(
        "mensaje de WhatsApp",
        max_length=200,
        default="Hola, quiero conversar sobre un proyecto.",
    )

    class Meta:
        verbose_name = "configuración del sitio"
        verbose_name_plural = "configuración del sitio"

    def __str__(self):
        return "Configuración del sitio"

    def save(self, *args, **kwargs):
        if self._state.adding and SiteSettings.objects.exists():
            raise ValidationError("Ya existe la configuración del sitio; edítala en vez de crear otra.")
        super().save(*args, **kwargs)

    @classmethod
    def current(cls):
        """Lectura sin escritura: el registro o una instancia sin guardar con valores por defecto."""
        obj = cls.objects.first()
        return obj if obj is not None else cls()

    @classmethod
    def load(cls):
        """Devuelve el único registro, creándolo si no existe."""
        obj = cls.objects.first()
        return obj if obj is not None else cls.objects.create()
