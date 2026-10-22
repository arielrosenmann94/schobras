import re

from django import forms
from PIL import Image, UnidentifiedImageError
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q

from core.models import SiteSettings
from core.whatsapp import normalize_number
from projects.models import Category, Project


class PanelAuthenticationForm(AuthenticationForm):
    """Ingreso con correo (o nombre de usuario); textos de docs/02-producto/textos-v1.md."""

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Correo o contraseña incorrectos.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Correo"


class OptionalOrderMixin:
    """El orden es opcional para la editora: vacío significa 0."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].required = False

    def clean_order(self):
        return self.cleaned_data.get("order") or 0


class CategoryForm(OptionalOrderMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "order", "is_active"]
        labels = {
            "name": "Nombre",
            "order": "Orden (número menor aparece primero)",
            "is_active": "Activa (aparece al crear proyectos)",
        }


class ProjectForm(OptionalOrderMixin, forms.ModelForm):
    construction_systems = forms.MultipleChoiceField(
        label="Sistemas constructivos",
        choices=Project.ConstructionSystem.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "category",
            "intervention_type",
            "commune",
            "region",
            "construction_systems",
            "area_m2",
            "year",
            "description",
            "is_featured",
            "order",
        ]
        labels = {
            "title": "Nombre del proyecto",
            "category": "Categoría",
            "intervention_type": "Tipo de intervención",
            "commune": "Comuna",
            "region": "Región",
            "area_m2": "Superficie (m²)",
            "year": "Año",
            "description": "Descripción",
            "is_featured": "Destacado en la portada",
            "order": "Orden (número menor aparece primero)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active = Q(is_active=True)
        if self.instance.category_id:
            active |= Q(pk=self.instance.category_id)
        self.fields["category"].queryset = Category.objects.filter(active)
        self.fields["category"].empty_label = "Elige una categoría"


MIN_PHONE_DIGITS = 8


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ["whatsapp", "phone", "email", "whatsapp_message"]
        labels = {
            "whatsapp": "WhatsApp",
            "phone": "Teléfono",
            "email": "Correo",
            "whatsapp_message": "Mensaje de WhatsApp",
        }
        help_texts = {
            "whatsapp": "Celular con o sin +56, por ejemplo +56 9 1234 5678. Si lo dejas vacío, el botón de WhatsApp no aparece en la web.",
            "phone": "Si lo dejas vacío, el teléfono no aparece en la web.",
            "email": "Si lo dejas vacío, el correo no aparece en la web.",
            "whatsapp_message": "Es el texto que ya viene escrito cuando alguien te abre el chat.",
        }

    def clean_whatsapp(self):
        value = self.cleaned_data["whatsapp"].strip()
        if value and not normalize_number(value):
            raise forms.ValidationError("Número de WhatsApp no válido. Ejemplo: +56 9 1234 5678")
        return value

    def clean_phone(self):
        value = self.cleaned_data["phone"].strip()
        if value and len(re.sub(r"\D", "", value)) < MIN_PHONE_DIGITS:
            raise forms.ValidationError("Teléfono no válido. Ejemplo: +56 9 1234 5678")
        return value


MAX_PHOTO_BYTES = 15 * 1024 * 1024
ALLOWED_PHOTO_FORMATS = {"JPEG", "PNG", "WEBP"}
FORMAT_ERROR = "Formato no soportado: sube fotos JPG, PNG o WebP."


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput)
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)) and data:
            return [single_clean(item, initial) for item in data]
        return [single_clean(data or None, initial)]


class PhotoUploadForm(forms.Form):
    images = MultipleImageField(
        label="Fotos",
        error_messages={"required": "Elige al menos una foto."},
    )

    def clean_images(self):
        errors = []
        for file in self.cleaned_data["images"]:
            if file.size > MAX_PHOTO_BYTES:
                errors.append(f"La foto {file.name} pesa más de 15 MB.")
                continue
            try:
                with Image.open(file) as image:
                    image_format = image.format
                    image.verify()
            except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError):
                errors.append(FORMAT_ERROR)
                continue
            finally:
                file.seek(0)
            if image_format not in ALLOWED_PHOTO_FORMATS:
                errors.append(FORMAT_ERROR)
        if errors:
            raise forms.ValidationError(list(dict.fromkeys(errors)))
        return self.cleaned_data["images"]
