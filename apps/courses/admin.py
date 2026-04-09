from django.contrib import admin

from apps.courses.models import Node, NodeNode, ClassGroupSyllabus


class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'type', 'grade_level', 'subject')

class NodeNodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent', 'child')

class CourseGroupSyllabusAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_group', 'node')

admin.site.register(Node, NodeAdmin)
admin.site.register(NodeNode, NodeNodeAdmin)
admin.site.register(ClassGroupSyllabus, CourseGroupSyllabusAdmin)