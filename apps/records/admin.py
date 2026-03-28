from django.contrib import admin

from apps.records.models import Attempt


class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'node', 'date', 'attempt')

admin.site.register(Attempt, AttemptAdmin)
