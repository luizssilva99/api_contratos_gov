from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'Perfil'
    verbose_name_plural = 'Perfil'
    fields = ('cargo', 'departamento')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_cargo', 'is_active')
    list_filter = ('is_active', 'is_staff')

    def get_cargo(self, obj):
        try:
            return obj.profile.cargo
        except UserProfile.DoesNotExist:
            return '-'
    get_cargo.short_description = 'Cargo'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Admin site customization
admin.site.site_header = 'GovAnalytics - Administração'
admin.site.site_title = 'GovAnalytics Admin'
admin.site.index_title = 'Painel de Administração'
