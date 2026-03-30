import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codeclique.settings')
django.setup()

from django.test import Client
c = Client()
try:
    response = c.get('/api/schema/')
    print(response.status_code)
    print(response.content.decode('utf-8')[:500])
except Exception as e:
    import traceback
    traceback.print_exc()
