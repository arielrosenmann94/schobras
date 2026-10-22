from django.db import migrations

CATEGORIES = [("Residencial", "residencial", 1), ("Comercial", "comercial", 2), ("Industrial", "industrial", 3)]


def create_categories(apps, schema_editor):
    Category = apps.get_model("projects", "Category")
    for name, slug, order in CATEGORIES:
        Category.objects.get_or_create(slug=slug, defaults={"name": name, "order": order})


def remove_categories(apps, schema_editor):
    Category = apps.get_model("projects", "Category")
    Category.objects.filter(slug__in=[slug for _, slug, _ in CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [("projects", "0001_initial")]
    operations = [migrations.RunPython(create_categories, remove_categories)]
