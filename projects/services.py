"""Única puerta de escritura para proyectos y fotos (ADR-0004)."""
from typing import Literal

from django.db import transaction
from django.db.models import Max

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


def add_photos(project: Project, files: list) -> list[ProjectPhoto]:
    with transaction.atomic():
        last = project.photos.aggregate(last=Max("order"))["last"] or 0
        has_cover = project.photos.filter(is_cover=True).exists()
        created = []
        for offset, file in enumerate(files, start=1):
            photo = ProjectPhoto.objects.create(
                project=project,
                image=file,
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


def delete_photo(photo: ProjectPhoto) -> None:
    with transaction.atomic():
        was_cover = photo.is_cover
        project_id = photo.project_id
        photo.delete()
        if was_cover:
            first = ProjectPhoto.objects.filter(project=project_id).first()
            if first:
                ProjectPhoto.objects.filter(pk=first.pk).update(is_cover=True)
