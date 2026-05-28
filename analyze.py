# analyze.py
import os
import json
from django.conf import settings
from django.apps import apps

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
import django
django.setup()

# Get project structure
project_info = {
    'project_name': os.path.basename(os.path.dirname(os.path.abspath(__file__))),
    'django_version': settings.VERSION,
    'installed_apps': settings.INSTALLED_APPS,
    'database': {
        'engine': settings.DATABASES['default']['ENGINE'].split('.')[-1],
        'name': settings.DATABASES['default'].get('NAME', 'Unknown'),
    },
    'base_dir': str(settings.BASE_DIR),
}

# Get all models
models_info = {}

for app_config in apps.get_app_configs():
    app_name = app_config.name
    models_info[app_name] = []

    for model in app_config.get_models():
        model_info = {
            'name': model.__name__,
            'db_table': model._meta.db_table,
            'fields': []
        }

        for field in model._meta.fields:
            field_info = {
                'name': field.name,
                'type': field.get_internal_type(),
                'max_length': field.max_length if hasattr(field, 'max_length') else None,
                'null': field.null,
                'blank': field.blank if hasattr(field, 'blank') else None,
                'default': str(field.default),
                'choices': field.choices if hasattr(field, 'choices') and field.choices else None,
            }
            model_info['fields'].append(field_info)

        models_info[app_name].append(model_info)

# Get URLs
from django.urls import get_resolver
urls_info = []
try:
    resolver = get_resolver()
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'pattern'):
            urls_info.append({
                'pattern': str(pattern.pattern),
                'name': pattern.name if hasattr(pattern, 'name') else None,
                'callback': str(pattern.callback) if hasattr(pattern, 'callback') else None,
            })
except Exception as e:
    urls_info = f'Error getting URLs: {str(e)}'

# Create output
output = {
    'project_overview': project_info,
    'models': models_info,
    'urls': urls_info,
}

# Save to file
with open('system_overview.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print('System overview saved to system_overview.json')
print(f'Project: {project_info["project_name"]}')
total_models = sum(len(models) for models in models_info.values())
print(f'Apps: {len(models_info)} apps with {total_models} models')