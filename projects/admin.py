from django.contrib import admin, messages

from . import services
from .models import Category, Project, ProjectPhoto


class ProjectPhotoInline(admin.TabularInline):
    model = ProjectPhoto
    extra = 1
    fields = ("image", "order", "is_cover", "alt_text", "kind")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "commune", "region", "status", "is_featured", "order")
    list_filter = ("status", "category", "region", "is_featured")
    search_fields = ("title", "commune")
    inlines = [ProjectPhotoInline]
    actions = ["publish_selected", "unpublish_selected"]

    @admin.action(description="Publicar proyectos seleccionados")
    def publish_selected(self, request, queryset):
        done = 0
        for project in queryset:
            try:
                services.publish(project)
            except services.PublishError as error:
                self.message_user(
                    request, f"{project.title}: {error}", level=messages.ERROR
                )
            else:
                done += 1
        if done:
            self.message_user(request, f"Proyectos publicados: {done}.")

    @admin.action(description="Despublicar proyectos seleccionados")
    def unpublish_selected(self, request, queryset):
        for project in queryset:
            services.unpublish(project)
        self.message_user(request, f"Proyectos despublicados: {queryset.count()}.")
