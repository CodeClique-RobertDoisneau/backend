from django.contrib import admin

from apps.courses.models import Node, NodeLink, ClassGroupSyllabus


class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'type', 'grade_level', 'subject')

class NodeLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent', 'child')

class CourseGroupSyllabusAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_group', 'node')

admin.site.register(Node, NodeAdmin)
admin.site.register(NodeLink, NodeLinkAdmin)
admin.site.register(ClassGroupSyllabus, CourseGroupSyllabusAdmin)