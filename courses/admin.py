from django.contrib import admin

from courses.models import Chapter, Section, Item

admin.site.register(Chapter)
admin.site.register(Section)
admin.site.register(Item)
