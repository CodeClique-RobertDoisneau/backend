from django.contrib import admin

from apps.users.models import User, ClassGroup, Membership


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')

class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_name', 'academic_year')

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'class_group', 'user_status')

admin.site.register(User, UserAdmin)
admin.site.register(ClassGroup, ClassGroupAdmin)
admin.site.register(Membership, MembershipAdmin)
