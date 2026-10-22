from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils import timezone

from core.models import BaseModel

from .utils import unique_slug


MIN_PROJECT_YEAR = 1950


def validate_project_year(value):
    """Año de la obra: desde 1950 hasta dos años más que el actual (obras en curso)."""
    max_year = timezone.localdate().year + 2
    if value is not None and not MIN_PROJECT_YEAR <= value <= max_year:
        raise ValidationError(
            f"El año debe estar entre {MIN_PROJECT_YEAR} y {max_year}.", code="year_range"
        )


DUPLICATE_CATEGORY_ERROR = "Ya existe una categoría con ese nombre."


class Category(BaseModel):
    name = models.CharField("nombre", max_length=80)
    slug = models.SlugField("slug", max_length=80, unique=True, editable=False)
    order = models.PositiveIntegerField("orden", default=0)
    is_active = models.BooleanField("activa", default=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["order", "name"]
        constraints = [
            # "Residencial" y "residencial" serían dos filtros casi iguales en la web.
            models.UniqueConstraint(
                Lower("name"),
                name="projects_category_name_ci_unique",
                violation_error_message=DUPLICATE_CATEGORY_ERROR,
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Category, self.name, max_length=80)
        super().save(*args, **kwargs)


class ProjectQuerySet(models.QuerySet):
    def published(self):
        """Proyectos públicos: publicados y con al menos una foto."""
        return self.filter(status=Project.Status.PUBLISHED, photos__isnull=False).distinct()


class Project(BaseModel):
    class InterventionType(models.TextChoices):
        NEW_BUILD = "new_build", "Obra nueva"
        EXTENSION = "extension", "Ampliación"
        REMODEL = "remodel", "Remodelación"

    class Region(models.TextChoices):
        METROPOLITANA = "metropolitana", "Región Metropolitana"
        VALPARAISO = "valparaiso", "Región de Valparaíso"
        OHIGGINS = "ohiggins", "Región de O'Higgins"

    class ConstructionSystem(models.TextChoices):
        MASONRY = "masonry", "Albañilería"
        REINFORCED_CONCRETE = "reinforced_concrete", "Hormigón armado"
        TIMBER = "timber", "Madera"
        VOLCOMETAL = "volcometal", "Volcometal"
        SIP_PANELS = "sip_panels", "Paneles SIP"
        STEEL = "steel", "Estructuras metálicas"

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PUBLISHED = "published", "Publicado"

    title = models.CharField("título", max_length=150)
    slug = models.SlugField("slug", max_length=170, unique=True, editable=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="projects",
        verbose_name="categoría",
    )
    intervention_type = models.CharField(
        "tipo de intervención", max_length=20, choices=InterventionType.choices
    )
    commune = models.CharField("comuna", max_length=80)
    region = models.CharField("región", max_length=20, choices=Region.choices)
    construction_systems = models.JSONField(
        "sistemas constructivos", default=list, blank=True
    )
    area_m2 = models.PositiveIntegerField("superficie (m²)", null=True, blank=True)
    year = models.PositiveSmallIntegerField(
        "año", null=True, blank=True, validators=[validate_project_year]
    )
    description = models.TextField("descripción", blank=True)
    status = models.CharField(
        "estado", max_length=12, choices=Status.choices, default=Status.DRAFT
    )
    is_featured = models.BooleanField("destacado en portada", default=False)
    order = models.PositiveIntegerField("orden", default=0)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        verbose_name = "proyecto"
        verbose_name_plural = "proyectos"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Project, self.title)
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        systems = self.construction_systems
        valid = set(self.ConstructionSystem.values)
        if not isinstance(systems, list) or any(item not in valid for item in systems):
            raise ValidationError(
                {"construction_systems": "Hay sistemas constructivos no válidos."}
            )

    def get_absolute_url(self):
        return reverse("projects:detail", args=[self.slug])

    @property
    def cover_photo(self):
        """Foto marcada como portada o, si no hay, la de menor orden."""
        photos = list(self.photos.all())
        for photo in photos:
            if photo.is_cover:
                return photo
        return photos[0] if photos else None

    def can_publish(self) -> bool:
        return self.photos.exists()

    @property
    def construction_systems_display(self) -> list[str]:
        labels = dict(self.ConstructionSystem.choices)
        return [labels[key] for key in self.construction_systems if key in labels]


class ProjectPhoto(BaseModel):
    class Kind(models.TextChoices):
        FINISHED = "finished", "Obra terminada"
        IN_PROGRESS = "in_progress", "En proceso"
        RENDER = "render", "Render"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="proyecto",
    )
    image = models.ImageField(
        "imagen",
        upload_to="proyectos/%Y/%m/",
        width_field="image_width",
        height_field="image_height",
    )
    image_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    order = models.PositiveIntegerField("orden", default=0)
    is_cover = models.BooleanField("portada", default=False)
    alt_text = models.CharField("texto alternativo", max_length=200, blank=True)
    kind = models.CharField("tipo", max_length=12, choices=Kind.choices, blank=True)

    class Meta:
        verbose_name = "foto"
        verbose_name_plural = "fotos"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.project.title} · foto {self.order}"

    @property
    def alt(self) -> str:
        return self.alt_text or self.project.title
