from django.shortcuts import get_object_or_404, render

from core.templatetags.image_tags import variant

from .models import Category, Project


def _public_projects():
    return Project.objects.published().select_related("category").prefetch_related("photos")


def _filter_categories():
    """Categorías activas que tienen al menos un proyecto público."""
    return Category.objects.filter(
        is_active=True, projects__in=Project.objects.published()
    ).distinct()


def _render_list(request, projects, active_category=None):
    return render(
        request,
        "projects/list.html",
        {
            "projects": projects,
            "categories": _filter_categories(),
            "active_category": active_category,
        },
    )


def project_list(request):
    return _render_list(request, _public_projects())


def project_category(request, slug):
    category = get_object_or_404(_filter_categories(), slug=slug)
    return _render_list(request, _public_projects().filter(category=category), category)


def project_detail(request, slug):
    project = get_object_or_404(_public_projects(), slug=slug)
    description = " ".join(project.description.split())
    cover = project.cover_photo
    return render(
        request,
        "projects/detail.html",
        {
            "project": project,
            "cover": cover,
            "photos": list(project.photos.all()),
            "meta_description": description[:155].rstrip() or f"{project.title} en {project.commune}.",
            "og_image": request.build_absolute_uri(variant(cover.image.url, 1200)) if cover else "",
        },
    )
