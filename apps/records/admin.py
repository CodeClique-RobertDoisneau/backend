from django.contrib import admin

from apps.records.models import Attempt, Progress


class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'node', 'date', 'attempt')

class ProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'node', 'started_at', 'completed_at', 'last_seen_at', 'status')

admin.site.register(Attempt, AttemptAdmin)
admin.site.register(Progress, ProgressAdmin)
