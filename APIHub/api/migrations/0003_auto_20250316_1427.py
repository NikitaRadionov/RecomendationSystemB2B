import json
import os
from django.db import migrations

def load_initial_data(apps, schema_editor):
    file_path = os.path.join(os.path.dirname(__file__), './../fixtures/initial_data.json')

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    for entry in data:
        model_name = entry["model"].split(".")[-1]
        Model = apps.get_model("api", model_name)

        fields = entry["fields"]
        m2m_fields = {}

        for field_name in list(fields.keys()):
            field = Model._meta.get_field(field_name)
            if field.many_to_many:
                m2m_fields[field_name] = fields.pop(field_name)

        for field_name, field_value in fields.items():
            field = Model._meta.get_field(field_name)
            if field.is_relation and not field.many_to_many and isinstance(field_value, int):
                related_model = field.related_model
                try:
                    fields[field_name] = related_model.objects.get(pk=field_value)
                except related_model.DoesNotExist:
                    print(f"Ошибка: Объект {related_model.__name__} с pk={field_value} не найден.")
                    continue

        if not Model.objects.filter(pk=entry["pk"]).exists():
            obj = Model.objects.create(**fields)

            for field_name, field_value in m2m_fields.items():
                m2m_field = getattr(obj, field_name)
                if field_value:
                    try:
                        m2m_field.set(field_value)
                    except Exception as e:
                        print(f"Ошибка при установке {field_name}: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_alter_order_okpd2"),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]
