from django.contrib import admin

from apps.courses.models import Chapter, Section, Item




class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'grade_level')

class SectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'difficulty')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'difficulty')

admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Item, ItemAdmin)