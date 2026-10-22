"""Única puerta de escritura para proyectos y fotos (ADR-0004)."""
import io
import os
from typing import Literal

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Max
from django.utils.text import slugify
from PIL import Image, ImageOps

from .models import Project, ProjectPhoto


class PublishError(Exception):
    """El proyecto no cumple las condiciones para publicarse."""


def publish(project: Project) -> None:
    if not project.can_publish():
        raise PublishError("Agrega al menos una foto antes de publicar.")
    project.status = Project.Status.PUBLISHED
    project.save(update_fields=["status", "updated_at"])


def unpublish(project: Project) -> None:
    project.status = Project.Status.DRAFT
    project.save(update_fields=["status", "updated_at"])


# Límites del plan de Cloudinary: 10 MB y 25 MP por imagen. Con 2560 px de
# lado mayor la foto queda en 6,5 MP como máximo y en pocos MB.
MAX_SIDE = 2560
MAX_STORED_BYTES = 10 * 1024 * 1024
JPEG_OPTIONS = {"format": "JPEG", "quality": 85, "optimize": True, "progressive": True}


def _has_transparency(image: Image.Image) -> bool:
    return image.mode in ("RGBA", "LA", "PA") or "transparency" in image.info


def _reencode(file) -> ContentFile:
    """Foto lista para guardar: orientada según EXIF, de máx. 2560 px y sin metadatos.

    JPEG de calidad 85, salvo imágenes con transparencia, que quedan en PNG
    (si el PNG pasara de 10 MB, se aplana sobre blanco y va como JPEG).
    El perfil de color ICC se conserva para no alterar los colores.
    """
    file.seek(0)
    with Image.open(file) as original:
        if original.format == "JPEG":
            original.draft("RGB", (MAX_SIDE, MAX_SIDE))
        icc_profile = original.info.get("icc_profile")
        transparent = _has_transparency(original)
        image = ImageOps.exif_transpose(original)
    image = image.convert("RGBA" if transparent else "RGB")
    image.thumbnail((MAX_SIDE, MAX_SIDE))

    output = io.BytesIO()
    extension = "jpg"
    if transparent:
        image.save(output, format="PNG", optimize=True, icc_profile=icc_profile)
        extension = "png"
        if output.tell() >= MAX_STORED_BYTES:
            flat = Image.new("RGB", image.size, "white")
            flat.paste(image, mask=image.getchannel("A"))
            image, output, extension = flat, io.BytesIO(), "jpg"
    if extension == "jpg":
        image.save(output, icc_profile=icc_profile, **JPEG_OPTIONS)

    base = slugify(os.path.splitext(os.path.basename(file.name or ""))[0])[:80] or "foto"
    return ContentFile(output.getvalue(), name=f"{base}.{extension}")


def add_photos(project: Project, files: list) -> list[ProjectPhoto]:
    """Agrega fotos ya validadas por el formulario, re-codificadas con _reencode."""
    with transaction.atomic():
        last = project.photos.aggregate(last=Max("order"))["last"] or 0
        has_cover = project.photos.filter(is_cover=True).exists()
        created = []
        for offset, file in enumerate(files, start=1):
            photo = ProjectPhoto.objects.create(
                project=project,
                image=_reencode(file),
                order=last + offset,
                is_cover=not has_cover and offset == 1,
            )
            created.append(photo)
    return created


def set_cover(photo: ProjectPhoto) -> None:
    with transaction.atomic():
        ProjectPhoto.objects.filter(project=photo.project_id).update(is_cover=False)
        ProjectPhoto.objects.filter(pk=photo.pk).update(is_cover=True)
    photo.is_cover = True


def move_photo(photo: ProjectPhoto, direction: Literal["up", "down"]) -> None:
    with transaction.atomic():
        photos = list(ProjectPhoto.objects.filter(project=photo.project_id))
        index = next(i for i, item in enumerate(photos) if item.pk == photo.pk)
        target = index - 1 if direction == "up" else index + 1
        if not 0 <= target < len(photos):
            return
        photos[index], photos[target] = photos[target], photos[index]
        for position, item in enumerate(photos, start=1):
            if item.order != position:
                ProjectPhoto.objects.filter(pk=item.pk).update(order=position)


def _delete_files_on_commit(storage, names: list[str]) -> None:
    """Borra los archivos solo si la transacción se confirma; una falla del storage queda en el log."""

    def delete_files():
        for name in names:
            storage.delete(name)

    if names:
        transaction.on_commit(delete_files, robust=True)


def delete_photo(photo: ProjectPhoto) -> None:
    with transaction.atomic():
        was_cover = photo.is_cover
        project_id = photo.project_id
        storage, name = photo.image.storage, photo.image.name
        photo.delete()
        _delete_files_on_commit(storage, [name])
        if was_cover:
            first = ProjectPhoto.objects.filter(project=project_id).first()
            if first:
                ProjectPhoto.objects.filter(pk=first.pk).update(is_cover=True)


def delete_project(project: Project) -> None:
    """Borra el proyecto, sus fotos y, al confirmar, los archivos de esas fotos."""
    with transaction.atomic():
        storage = ProjectPhoto._meta.get_field("image").storage
        names = [photo.image.name for photo in project.photos.all() if photo.image.name]
        project.delete()
        _delete_files_on_commit(storage, names)
