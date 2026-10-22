from django import forms
from PIL import Image, UnidentifiedImageError
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q

from projects.models import Category, Project


class PanelAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Usuario o contraseña incorrectos.",
    }


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
